from soccer_network.data import (match_ids, huskies_player_ids, huskies_events, huskies_passes, matches_df, all_events,
                                 events_df)
from soccer_network.graphs import load_graphml
from graph_tool import Graph, clustering, correlations, centrality, VertexPropertyMap
import pandas as pd
import numpy as np
from typing import Tuple, List, Callable, Any

"""
centrality
correlations
flow
dynamics
configuration model
topology
"""


def get_mean_std_of_scalar_vertex_properties(vps: List[VertexPropertyMap]):
    data = [r.get_array() for r in vps]
    data = np.asarray(data)
    mean = np.mean(data, axis=1)
    std = np.std(data, axis=1)
    return mean, std


def clustering_coefficient(g: Graph):
    return clustering.local_clustering(g, weight=g.edge_properties['weight'], undirected=False)


def post_clustering_coefficient(results):
    mean, std = get_mean_std_of_scalar_vertex_properties(results)
    df = pd.DataFrame(dict(MatchID=match_ids, cc_mean=mean, cc_std=std))
    df = matches_df[['Outcome', 'OwnScore']].join(df, how='right')
    print(df.corr())
    return mean, std


def passing_volume(g: Graph):
    vs = g.get_vertices()
    total = g.get_total_degrees(vs, g.edge_properties['weight'])
    return np.mean(total), np.std(total)


def post_passing_volume(results: Tuple):
    # from matplotlib import pyplot as plt
    mean, sigma = zip(
        *results)  # https://stackoverflow.com/questions/13635032/what-is-the-inverse-function-of-zip-in-python
    df = pd.DataFrame(dict(MatchID=match_ids, pv_mean=mean, pv_sigma=sigma))
    df = matches_df[['Outcome', 'OwnScore']].join(df, how='right')
    print(df.corr())


def assortativity(g: Graph):
    return correlations.assortativity(g, 'total', g.edge_properties['weight'])


def post_assortativity(results):
    mean, variance = zip(*results)
    df = pd.DataFrame(dict(MatchID=match_ids, assort_mean=mean, assort_var=variance))
    df = matches_df[['Outcome', 'OwnScore']].join(df, how='right')
    print(df.corr())


def motifs(g: Graph, k: int = 3):
    return clustering.motif_significance(g, k)


def post_motifs(results: List[Tuple]):
    sorted_zs = []
    for mn, z in results:
        z = np.asarray(z)
        z[::-1].sort()
        sorted_zs.append(z)
    print(sorted_zs)
    return sorted_zs


def pagerank_centrality(g: Graph):
    return centrality.pagerank(g, weight=g.edge_properties['weight'])


def post_pagerank_centrality(results):
    mean, std = get_mean_std_of_scalar_vertex_properties(results)
    df = pd.DataFrame(dict(MatchID=match_ids, pagerank_mean=mean, pagerank_std=std))
    df = matches_df[['Outcome', 'OwnScore']].join(df, how='right')
    print(df.corr())
    return mean, std


# TODO: add your metrics here, the function should have only one required argument and can return anything you like
metrics: List[Callable] = [
    passing_volume,
    clustering_coefficient,
    motifs,
    assortativity,
    pagerank_centrality,
]

# TODO| add your post-metrics-computation processing function here,
# the results of every metric **for all graphs** are passed in as **one** single argument
# NOTE: the order of results is the same as the order of `match_ids`
post_metrics: List[Callable] = [
    post_passing_volume,
    post_clustering_coefficient,
    post_motifs,
    post_assortativity,
    post_pagerank_centrality,
]


def run_metric(gs: List[Graph], metric: Callable[[Graph], Any], post_metric: Callable):
    print('Running {0}'.format(metric.__name__))
    results = [metric(g) for g in gs]
    print('Running {0}'.format(post_metric.__name__))
    post_metric(results)


if __name__ == "__main__":
    print('Loading graphml files...')
    graphs = [load_graphml('../graphs/network-{0}.xml'.format(mi)) for mi in match_ids]
    # graphs = [load_graphml('../graphs/zoned-network-{0}.xml'.format(mi)) for mi in match_ids]

    print('Calculating metrics...')
    # run a single metric
    run_metric(graphs, pagerank_centrality, post_pagerank_centrality)

    # or run all metrics
    # for m, pm in zip(metrics, post_metrics):
    #     run_metric(graphs, m, pm)
