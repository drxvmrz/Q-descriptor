# 🎭 Q-descriptor calculations

Python scripts and database for monoclinic-to-orthorhombic Q-descriptor calculation for  
*CCDC-2023 ([The Cambridge Crystallographic Data Centre](https://www.ccdc.cam.ac.uk/structures/))* crystals may undergo 
structural monoclinic-to-orthorhombic second-order phase transition.  

## 🏛️ Introduction

Q-descriptor is defined as  

$$ Q_{\beta}(m, n, p, q) = \frac{1}{1} $$  

and

$$ Q_{\gamma}(m, n, p, q) = \frac{1}{1} $$  

for $\beta$ and $\gamma$ monoclinic angle setup respectively. Where $m, n, p, q$ just are undefined coefficients that take  
integer values and $\pm 0.5$. Constants $a, b, c, \beta, \gamma$ are values of cell parameters of corresponding crystal structure.

This allows to determine whether it is possible to construct an orthorhombic basis on the translations of the initial monoclinic lattice   
so that forms a supergroup for the translations of the original monoclinic ones. This is possible if one can find numbers $m, n, p, q$ such
that $Q(m, n, p, q) \in [0.000, 0.079]$.  

Coefficients $m, n, p, q$ express the vectors of the initial monoclinic basis in terms of the vectors $\vec{u}$ and $\vec{v}$ of the new orthorhombic basis as  

$$ 123 $$

## 👨🏻‍🎓 Original article

This repository represents an application for original [article](https://www.doi.org).  
If this database or scripts are useful in your academic research, please cite:

> In process ...

## 💎 Database manual


## 📚 How scripts work

