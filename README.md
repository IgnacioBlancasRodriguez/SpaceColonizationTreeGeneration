# Space Colonization and Generalized Cylinders for Tree Generation in Python

The following project explores the use of the Space Colonization Algorithm for tree generation and goes forward to use $C^2$ BSplines and Generalized Cylinders to generate 3Dimentional trees.

The project follows some of the notions outlied in [Modeling Trees with a Space Colonization Algorithm, 2007](http://algorithmicbotany.org/papers/colonization.egwnp2007.large.pdf); [Modeling the Mighty Mapple, 1985](https://courses.cs.duke.edu/fall01/cps124/resources/p305-bloomenthal.pdf); [Generating a 3D growing tree using a space colonization algorithm, 2019](https://ciphrd.com/2019/09/11/generating-a-3d-growing-tree-using-a-space-colonization-algorithm/); and [The Continuity of Splines, 2022](https://www.youtube.com/watch?v=jvPPXbo87ds).

### 1. Optimizations
#### 1.1 Optimizations on the Space Colonization Algorithm
In order to avoid repeated computation and accelerate the tree skeleton generation, on every iteration only those nodes that have been associated to one or more attractors will be visited when generating new nodes, instead of visiting all of the attractors. In cases were several attractors have been associated to a singular node, this reduces the amount of times a node is visited.
#### 1.2 Optimizations on the BSplines
To accelerate the BSplines, as I am using a uniform BSplines, my basis functions stay the same accross the whole curve and thus I could build a matrix to represent the curve in its matrix form, that would stay consistent along the whole curve. In order for the curve to achieve $C^2$ continity a system of 16 by 16 equations is solved to yield the following matrix:
$$
\begin{bmatrix}
    \frac{1}{6} & \frac{2}{3} & \frac{1}{6} & 0 \\
    \frac{-1}{2} & 0 & \frac{1}{2} & 0 \\
    \frac{1}{2} & -1 & \frac{1}{2} & 0 \\
    \frac{-1}{6} & \frac{1}{2} & \frac{-1}{2} & \frac{1}{6}
\end{bmatrix}
$$
$$P(t)=
\begin{bmatrix}
    1 & t & t^2 & t^3
\end{bmatrix}
\begin{bmatrix}
    \frac{1}{6} & \frac{2}{3} & \frac{1}{6} & 0 \\
    \frac{-1}{2} & 0 & \frac{1}{2} & 0 \\
    \frac{1}{2} & -1 & \frac{1}{2} & 0 \\
    \frac{-1}{6} & \frac{1}{2} & \frac{-1}{2} & \frac{1}{6}
\end{bmatrix}$$
#### 1.3 Optimizations on the branch radiuses
As the radiuses will be computed recursively, in order to avoid repeated computation, I use memoization, by saving each computed radius in its corresponings node inner data.