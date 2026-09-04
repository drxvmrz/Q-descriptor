# 🎭 Q-descriptor calculations

Python scripts and database for monoclinic-to-orthorhombic Q-descriptor calculation for *CCDC-2023 ([The Cambridge Crystallographic Data Centre](https://www.ccdc.cam.ac.uk/structures/))* crystals may undergo 
structural monoclinic-to-orthorhombic second-order phase transition.  

## 🏛️ Background

Q-descriptor is defined as  

$$ Q_{\beta}(m, n, p, q) = \frac{1}{1} $$  

and

$$ Q_{\gamma}(m, n, p, q) = \frac{1}{1} $$  

for $\beta$ and $\gamma$ monoclinic angle setup respectively. Where $m, n, p, q$ just are *integer or half-integer* coeffitients. Constants $a, b, c, \beta, \gamma$ are values of cell parameters of corresponding crystal structure.

This allows to determine whether it is possible to construct an orthorhombic basis on the translations of the initial monoclinic lattice so that forms a supergroup for the translations of the original monoclinic ones. This is possible if one can find numbers $m, n, p, q$ such that  

$$ Q(m, n, p, q) \in [0.000, 0.079]. $$  

Coefficients $m, n, p, q$ express the vectors of the initial monoclinic basis in terms of the vectors $\vec{u}$ and $\vec{v}$ of the new orthorhombic basis. For example, for *mineralogic setup* (monoclinic angle $\beta$) it looks like  

$$ \begin{cases}
\vec{a} = m \cdot \vec{u} + n \cdot \vec{v} \\
\vec{c} = p \cdot \vec{u} + q \cdot \vec{v}
\end{cases}, $$

for *rational setup* (monoclinic angle $\gamma$) it will be vector $\vec{b}$ instead of $\vec{c}$. The 3-rd translation is transferred from initial monoclinic cell. Neccessary condition for $\vec{u}$ and $\vec{v}$ is  

$$ (\vec{u} \cdot \vec{v}) \approx 0.$$  

In monoclinic and orthorhombic symmetry only mirror planes and 2-fold axes are allowed. In orthorhombic cell these symmetry operators can only be located parallel or perpendicular to the translations. The presence of pseudosymmetry elements, involving translations $\vec{u}$ and $\vec{v}$ as well as the corresponding mirror planes and axes, may indicate a close structural relationship with a higher-symmetry orthorhombic phase. 

This suggests that the crystal could potentially undergo a second-order monoclinic-to-orthorhombic phase transition, in line with the group-subgroup requirements of Landau theory.

## 👨🏻‍🎓 About this work

This repository contains the code and database developed as part of the author's 
PhD research. The underlying method is described in the dissertation:

> Drozhilkin, P. D. (2026). *DEVELOPMENT OF QUANTITATIVE METHODS FOR DESCRIBING THE ATOMIC STRUCTURES OF COORDINATION COMPOUNDS AND ORGANIC CRYSTALS SUBJECT TO SECOND-ORDER STRUCTURAL PHASE TRANSITIONS* (in preparation). 
> Lobachevsky State University of Nizhny Novgorod, Russia.

## 📚 Calculate your own database

The main script is [calc_descriptor.py](https://github.com/drxvmrz/Q-descriptor/blob/main/scripts/calc_descriptor.py). It represents a front-end for [APEXSYMM](https://github.com/drxvmrz/apexsymm) calculation kernel.

## 💎 CCDC database checking



