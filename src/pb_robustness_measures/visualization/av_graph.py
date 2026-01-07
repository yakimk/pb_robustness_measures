from collections.abc import Collection
from pabutools.rules.budgetallocation import BudgetAllocation
from pabutools.election import Instance, Project, total_cost, AbstractApprovalProfile
from pabutools.tiebreaking import TieBreakingRule, lexico_tie_breaking
import matplotlib.pyplot as plt

def av_graph(
    instance: Instance,
    profile: AbstractApprovalProfile,
    tie_breaking: TieBreakingRule | None = None,
    show_labels: bool = True,
    name: str = "",
    projects: int = 0,
    voters : int =0, 
    budget : int =0, 
    save_path: str | None = None,
    ):
    """
    Given an instance produces a graph of (supperters, cost) for each project
    and draws a curve of (move, budget left).
    As a conseqeunce of this definition every project lying below the curve will be selected by 
    Seq - AV. 

    Also several measures on AV can be interpreted by looking at this graph.
    For instance `optimal cost` is simply a vertical projection of a point onto a curve
    `optimal approval` is horizontal projection.


    After choosing appropriate coordinates (i.e. deciding on how much one new voter costs for example)
    We might also consider measure that is the distance to the curve. 
    But note that for every project this measure would be dependent on the choice of coordinates.
    But after choice of coordinates for each candidate the measure of distance to the graph is well-defined. 
    We might call it "subjective stability" or "perceived stability" (as it depends on the choice of coordinates by candidate).
    The point on the curve that is the projection for a given candidate is called optimal (it need not be unique of course).

    We can also define a measure of `rivalry` in terms of "how many optimal points 
    of other candidates are close to my optimal point". A kind of naive approach would be 
    to define it as a length of an arc of the curve (centered at an optimal point for a chosen candidate) 
    that contains for example 10% of optimal points for other candidates or something like that. 

    Also this allows us to define what we call `fundamental region` of an election,
    which is simply (don't know what it represents yet, but seems interesting)
    """
    if tie_breaking is None:
        tie_breaking = lexico_tie_breaking

    allocation = BudgetAllocation()
    # current_cost = total_cost(allocation)
    remaining = [p for p in instance if p not in allocation]
    scores = {p: profile.approval_score(p) for p in remaining}
    ordered: list[Project] = []
    to_order = set(remaining)
    while to_order:
        max_score = max(scores[p] for p in to_order)
        tied = [p for p in to_order if scores[p] == max_score]
        ordered_ties = tie_breaking.order(instance, profile, tied)
        ordered.extend(ordered_ties)
        to_order.difference_update(tied)

    supporters = [profile.approval_score(p) for p in ordered]
    costs = [p.cost for p in ordered]
    names = [p.name for p in ordered]

    budget_levels = []
    selected = []
    remaining_budget = instance.budget_limit
    for p in ordered:
        budget_levels.append(remaining_budget)
        if profile.approval_score(p) > 0 and remaining_budget >= p.cost:
            selected.append(True)
            remaining_budget -= p.cost
        else:
            selected.append(False)

    fig, ax = plt.subplots(figsize=(9,5.5))
    colors = ['blue' if sel else 'red' for sel in selected]
    ax.scatter(supporters, costs, c=colors)
    if show_labels:
        for x, y, label in zip(supporters, costs, names):
            ax.annotate(label, (x, y), textcoords="offset points", xytext=(5,5))

    x0, x1 = supporters[0] + 1, supporters[0]
    start, end = max(x0, x1), min(x0, x1)
    ax.hlines(budget_levels[0], start, end)

    for i, y in enumerate(budget_levels):
        if i > 0:
            x0, x1 = supporters[i-1], supporters[i]
            start, end = max(x0, x1), min(x0, x1)
            ax.hlines(y, start, end)

    for i in range(len(supporters)-1):
        x = supporters[i]
        y0 = budget_levels[i]
        y1 = budget_levels[i+1]
        bottom, top = min(y0, y1), max(y0, y1)
        ax.vlines(x, bottom, top)

    ax.set_xlabel('Number of Supporters', fontsize=14)
    ax.set_ylabel('Project Cost', fontsize=14)
    vote = f" | Voters: {voters}" if voters > 0 else ""
    proj = f" | Projects: {projects}" if projects > 0 else ""
    budg = f" | Budget: {int(budget)}" if budget > 0 else ""
    if name:
        ax.set_title(name.replace("_", " ") + vote + proj + budg)
    else:
        ax.set_title(vote + proj + budg)
    ax.invert_xaxis()
    
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()
