import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd
from . import utils
from ..preprocessing.simple import normalize_per_cell
from ..utils import doc_params
from .docs import doc_show_save_ax


@doc_params(show_save_ax=doc_show_save_ax)
def highest_expr_genes(adata, n_top=30, show=None, save=None, ax=None, **kwds):
    """\
    Fraction of counts assigned to each gene over all cells.

    Computes, for each gene, the fraction of counts assigned to that gene within
    a cell. The `n_top` genes with the highest mean fraction over all cells are
    plotted as boxplots.

    This plot is similar to the `scater` package function `plotQC(type =
    "highest-expression")`, see `here
    <https://bioconductor.org/packages/devel/bioc/vignettes/scater/inst/doc/vignette-qc.html>`__.

    Parameters
    ----------
    adata : :class:`~anndata.AnnData`
        Annotated data matrix.
    n_top : `int`, optional (default:30)
        Number of top
    {show_save_ax}
    **kwds : keyword arguments
        Are passed to `seaborn.boxplot`.

    Returns
    -------
    If `show==False` a `matplotlib.Axis`.
    """
    from scipy.sparse import issparse

    # compute the percentage of each gene per cell
    dat = normalize_per_cell(adata, counts_per_cell_after=100, copy=True)

    # identify the genes with the highest mean
    if issparse(dat.X):
        dat.var['mean_percent'] = dat.X.mean(axis=0).A1
        top = dat.var.sort_values('mean_percent', ascending=False).index[:n_top]
        dat = dat[:, top]
        dat = pd.DataFrame(dat.X.toarray(), index=dat.obs_names, columns=dat.var_names)

    else:
        dat.var['mean_percent'] = dat.X.mean(axis=0)
        top = dat.var.sort_values('mean_percent', ascending=False).index[:n_top]
        dat = dat[:, top]
        dat = pd.DataFrame(dat.X, index=dat.obs_names, columns=dat.var_names)

    if not ax:
        # figsize is hardcoded to produce a tall image. To change the fig size,
        # a matplotlib.Axes object needs to be passed.
        height = (n_top * 0.2) + 1.5
        fig, ax = plt.subplots(figsize=(5, height))
    sns.boxplot(data=dat, orient='h', ax=ax, fliersize=1, **kwds)
    ax.set_xlabel("% of total counts")
    utils.savefig_or_show('highest_expression', show=show, save=save)
    return ax if show == False else None
