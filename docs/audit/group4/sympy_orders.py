import sympy as sp
h,y,S,a,b=sp.symbols('h y S a b',positive=True)
v=h**2*S/(S+h**2); m=S*y/(S+h**2)          # h-tilted law of Y (Gaussian design N(0,S))
# nonlinear mean mu(Y)=Y+a Y^2 ; hetero Sigma(Y)=1+b Y^2
VarMu=v+4*a*m*v+a**2*(4*m**2*v+2*v**2)
print("Var_h[mu(Y)] series:", sp.series(sp.simplify(VarMu),h,0,5))
print("  predicted h^2 J^2 =", sp.expand(h**2*(1+2*a*y)**2))
EH=1+b*(m**2+v)
ser=sp.series(EH,h,0,4).removeO()
print("E_h[Sigma(Y)] series:", sp.expand(ser))
s=-y/S   # grad log rho
print("  predicted h^2[Sigma' s + Sigma''/2] =", sp.expand(h**2*(2*b*y*s+b)))
