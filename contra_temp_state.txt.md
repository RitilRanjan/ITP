# Environment State

This file contains the saved state of the theorem prover.

## Ground Environment

- **Variables**: x, y
- **Theorems**: 0

---

## Child Environment (Goal: f4)

- **Variables**: None
- **Theorems**: 1

### Proven Theorems
- **f2**: ¬ <span style="color: #00FFFF">(</span><span style="color: #FF00FF"> x = x </span><span style="color: #00FFFF">)</span>

---

## Data Payload
```itp
[Environment 0]
Goal: None
Original Goal: None
And Right: None
Target Proven: None
Variables: 
Dummy Variables: 
Meta Variables: 
Propositional Variables: 
User Functions:
User Relations:
Terms:
Formulae:
  f1 | x = x
  f3 | x ∈ x
Theorems:

[Environment 1]
Goal: f4
Original Goal: f4
And Right: None
Target Proven: f1
Variables: 
Dummy Variables: 
Meta Variables: 
Propositional Variables: 
User Functions:
User Relations:
Terms:
Formulae:
  f2 | ¬ ( x = x )
  f4 | ¬ ( x ∈ x ) ∧ ( x ∈ x )
Theorems:
  f2 | ¬ ( x = x )

```
