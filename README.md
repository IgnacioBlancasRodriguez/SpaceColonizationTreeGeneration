# Space Colonization and Generalized Cylinders for Tree Generation in Python

The following project explores the use of the Space Colonization Algorithm for tree generation and goes forward to use $C^2$ BSplines and Generalized Cylinders to generate 3Dimentional trees.

The project follows some of the notions outlied in [Modeling Trees with a Space Colonization Algorithm, 2007](http://algorithmicbotany.org/papers/colonization.egwnp2007.large.pdf); [Modeling the Mighty Mapple, 1985](https://courses.cs.duke.edu/fall01/cps124/resources/p305-bloomenthal.pdf); [Generating a 3D growing tree using a space colonization algorithm, 2019](https://ciphrd.com/2019/09/11/generating-a-3d-growing-tree-using-a-space-colonization-algorithm/); and [The Continuity of Splines, 2022](https://www.youtube.com/watch?v=jvPPXbo87ds).

### 1. Optimizations
#### 1.1 Optimizations on the Space Colonization Algorithm
In order to avoid repeated computation and accelerate the tree skeleton generation, on every iteration only those nodes that have been associated to one or more attractors will be visited when generating new nodes, instead of visiting all of the attractors. In cases were several attractors have been associated to a singular node, this reduces the amount of times a node is visited.
#### 1.2 Optimizations on the BSplines
To accelerate the BSplines, as I am using a uniform BSplines, my basis functions stay the same accross the whole curve and thus I could build a matrix to represent the curve in its matrix form, that would stay consistent along the whole curve. In order for the curve to achieve $C^2$ continity a system of 16 by 16 equations is solved to yield the following matrix:
```math
\begin{bmatrix}
    \frac{1}{6} & \frac{2}{3} & \frac{1}{6} & 0 \\
    \frac{-1}{2} & 0 & \frac{1}{2} & 0 \\
    \frac{1}{2} & -1 & \frac{1}{2} & 0 \\
    \frac{-1}{6} & \frac{1}{2} & \frac{-1}{2} & \frac{1}{6}
\end{bmatrix}
```
```math
P(t)=
\begin{bmatrix}
    1 & t & t^2 & t^3
\end{bmatrix}
\begin{bmatrix}
    \frac{1}{6} & \frac{2}{3} & \frac{1}{6} & 0 \\
    \frac{-1}{2} & 0 & \frac{1}{2} & 0 \\
    \frac{1}{2} & -1 & \frac{1}{2} & 0 \\
    \frac{-1}{6} & \frac{1}{2} & \frac{-1}{2} & \frac{1}{6}
\end{bmatrix}
```
#### 1.3 Optimizations on the branch radiuses
As the radiuses will be computed recursively, in order to avoid repeated computation, I use memoization, by saving each computed radius in its corresponings node inner data.

### 2. Generalized Cylinders
In order to add volume to our tree we will be using generalized cylinders. The cylinder will be made up of circles centered on each node and porjected on the plane whose normal vector is the vector tangent to the skeleton at the coordinates of the given node.

In order to do project each circle on its respective plane, we will be calculating two basis vectors in that plane. We will do so by rotating the vectors $\vec{i}$, and $\vec{j}$ along the skeleton. This alone, however, may lead to unnecesary twisting where the tangent vectors between two nodes change direction from a downward pointing one to an upward pointing one. In order to mitigate this, each time a refference frame is calculated, we will save its respective $\vec{i}$, $\vec{j}$, and $\vec{T}$, also reffered to as, $\vec{B}$, $\vec{N}$, and $\vec{T}$ vectors, and calculating the new refference frames based on those of its children node. This is done by generating the quaternion representing the rotation from the children node's $\vec{T}$ and the current node's $\vec{T}$ vector, and then applying these to the children node's $\vec{B}$, and $\vec{N}$ vectors, to form the current node's respective vectors.

We will use the following procedure to calculate the quaternion representing the rotation from un vector to another one:
```math
q = cos(\alpha) + sin(\alpha)\cdot(a\vec{i} + b\vec{j} + c\vec{k})
```
```math
a\vec{i} + b\vec{j} + c\vec{k} = \vec{T} \times \vec{T_{prev}}
```
```math
\alpha = tan^{-1}(\frac{\lvert \vec{T} \times \vec{T_{prev}} \rvert}{\vec{T} \cdot \vec{T_{prev}}})
```