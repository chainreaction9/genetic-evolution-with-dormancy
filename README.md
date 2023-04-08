A genetic model with dormancy
=============================

If you are here after watching this [simulation](https://chainserver.pythonanywhere.com/hiv-dormancy), you may have found the variations in activity level of the viral motions rather strange:
<i>
the purple ones are moving in the 3D space in a spontaneous manner, whereas the green ones stay still!
</i>
What's even more interesting is that a purple virus may turn into a green one and vice versa. The purple ones can also give birth to new offsprings until they exhaust the viral capacity of the geographic space. The motivation for considering such a system comes from *microbial dormancy*, a biological trait where organisms enter into a state of reduced or no activity at all.
In our case a key characteristic of the green type of virus is that it stays at the same initial geographic position up to the time before turning back into a purple one again. This can also be modified to incorporate *soft dormancy* by allowing the green types move at a potentially slower speed than the purple ones.
The way the transformation from one type of virus to the other occurs is quite simple, well, at least mathematically so if not biologically: each purple virus is assigned a time interval of random length having an exponential distribution of mean 1 during which the virus performs Brownian motion in the 3D space; after the end of the time interval it becomes green or rather *dormant* per se, and is assigned a new time interval of random length at the end of which it turns back into the purple type again.
This model, although looks good in the [simulation](https://chainserver.pythonanywhere.com/hiv-dormancy), does not incorporate either soft dormancy or interactions among the viral entities. In real life the situation is far more complicated, even more so when there is an underlying **network structure** via which the viral entities influence each other.
Therefore, a better approach would be to consider *spatially structured* several colonies of viral entities which can interact with the others via some simpler mechanism. Addition of simple interactions such as *resampling* of genotypes, or more precisely, *mimicry* of biological traits, etc. can make the model even more realistic. This is exactly what we are going to introduce below.

## Model description
Consider a finite collection of colonies consisting of viral entities that carry either genotype A (red) or genotype B (white). A viral entity can either be in an active or a dormant state. Each colony accomodates at most a preassigned finite number of active and dormant viral entities. Moreover, genetic evolution takes place with time as the viral entities that are not dormant continue to resample/mimic genotypes from their own as well as other colonies.
A clear consequence of the finite viral capacity and the mimicry of genotypes is that only one of the two genotypes A (red) and B (white) survives till the end. But which one of the two does is not easy to answer, at least analytically, because of the intrinsic randomness. Here, we simulate this model on a 2D torus, where each colony has two subpopulations of fixed size consisiting of the active and the dormant viral entities. 
After certain random time intervals, active viral entities change their genotype by resampling a random genotype from the active subpopulations. The probability of choosing a particular active subpopulation during the resampling events depends on certain preassigned interaction strength parameters that we call the *migration kernel*. Further, we consider simultaneous switching between active and dormant viral entities: *when an active viral entity becomes dormant, another dormant one randomly chosen from the same colony wakes up and vice versa. The genotypes of the viral entities are preserved while the simultaneous switching takes place.*

## Simulation
<p align="center">
  <img alt="Webapp img" src="/cluster.gif"/>
</p>
In this project the above model is simulated with 4 colonies where the sizes of the populations are sampled beforehand from a Geometric distribution. The red color concentration in each colony/grid represents its present percentage amount of the type A (red) viral entities. The white ones eventually get extinct and the red ones survive, although the red types were already extinct in the active part of the geographic space at a certain time point. The randomly fluctuating <i>purple</i> (resp. <i>green</i>) line shows the <strong>average number (in percentage) of type A (red) viral entities</strong> in the <i>active</i> (resp. <i>dormant</i>) part of the entire geographic space.

### Dependency
To run the simulation the following dependencies must be available in the python (minimum version 3.0) dev environment.
1. imageio
2. matplotlib
3. numpy
4. pygame

These can be installed with the following command:
```bash
pip install -r requirements.txt
````

To play the simulation, run the following command from the project root directory in the bash console, or command prompt:
```
python geneticModel.py
```
To save images from the simulation, one can set the &ldquo;Save image&rdquo; flag to True and make sure that the output directory defined by the `FOLDER_NAME` variable (is set to &ldquo;image&rdquo; by default) already exists. These images can later be used to create a GIF using the provided python script &ldquo;generateGIF.py&rdquo;.

## Acknowledgements
The genetic model considered here was analyzed as a part of the author's doctoral thesis and is based on the following joint works with his supervisors and collaborators:
1. [Spatially Inhomogeneous Populations with Seed-Banks: I. Duality, Existence and Clustering](https://link.springer.com/article/10.1007/s10959-021-01119-z)
2. [Spatially Inhomogeneous Populations with Seed-Banks: II. Clustering Regime](https://doi.org/10.1016/j.spa.2022.04.010)
3. [Spatial Populations with Seed-Banks in Random Environment: III. Convergence towards Mono-Type Equilibrium](https://doi.org/10.1214/23-EJP922)
4. [Switching Interacting Particle Systems: Scaling Limits, Uphill Diffusion and Boundary Layer](https://link.springer.com/article/10.1007/s10955-022-02878-7)
