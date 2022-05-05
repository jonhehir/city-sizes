*This is a dump of the code accompanying a paper that analyzes the distribution of US city sizes over various city definitions. This code was originally written around 2017-2018 in collaboration with [Shiguo Jiang](https://www.albany.edu/spatial/jiang/) at the University at Albany, SUNY.*

# Background

Economic research has pointed out that city sizes often follow [an interesting pattern](https://en.wikipedia.org/wiki/Rank%E2%80%93size_distribution): the size of the *n*-th city is approximately 1/*n* times the size of the largest city. In other words, the second-biggest city is about half the size of the largest, the third-biggest is about one third, and so on. For example, the largest cities of the US, [per Wikipedia](https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population):

City        | Population | As a Fraction of the Largest
------------|------------|-----------------------------
New York    | 8,175,133  | 100%
Los Angles  | 3,792,621  | 46% *(approx. 1/2)*
Chicago     | 2,695,598  | 33% *(approx. 1/3)*
Houston     | 2,099,451  | 26% *(approx. 1/4)*

The extent to which this phenomenon holds appears to depend on a variety of factors, especially:

- how a city is defined (municipal boundaries, metro area, etc.)
- how far down the list you look (truncation point)
- the statistical goodness-of-fit method used.

## City Clustering Algorithm

Competing city definitions are somewhat arbitrary. The city clustering algorithm (CCA) of [Rozenfeld et al.](https://www.aeaweb.org/articles?id=10.1257/aer.101.5.2205) aims to create a definition of the city that is free of arbitrary legal boundaries by clustering Census tracts into natural areas. Variants of the city clustering algorithm have been developed based on alternative data sources.

# The Code

This dump includes the code used to generate a new variant of CCA, based on Census block data. It is a spatially-aware hierarchical clustering algorithm that clusters Census blocks in excess of a given density threshold (d_min) whose borders are within a prescribed distance (l).

This dump also includes code used to compare the results of various city definitions and to evaluate their goodness-of-fit through a rigorous bootstrap-based process as prescribed by [Clauset et al.](https://epubs.siam.org/doi/abs/10.1137/070710111).
