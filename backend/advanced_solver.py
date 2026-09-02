import re, math
import sympy as sp

def symbolic_solve(equation: str, variable: str):
    """Solve a user-supplied algebraic equation safely with SymPy."""
    try:
        x=sp.Symbol(variable)
        cleaned=equation.replace("^","**")
        if "=" in cleaned:
            left,right=cleaned.split("=",1)
            expr=sp.sympify(left, locals={variable:x})-sp.sympify(right, locals={variable:x})
        else:
            expr=sp.sympify(cleaned, locals={variable:x})
        return [str(s) for s in sp.solve(expr,x)]
    except Exception:
        return []

def common_solver(text: str):
    q=text.lower().replace("×","*")
    nums=[float(x) for x in re.findall(r"(?<![a-z])\d+(?:\.\d+)?",q)]
    # momentum p = mv
    if ("momentum" in q or "كمية الحركة" in q) and len(nums)>=2:
        m,v=nums[0],nums[1]
        return {"topic":"momentum","equation":"p = mv","result":m*v,
                "unit":"kg·m/s","steps":[f"p = {m} × {v}",f"p = {m*v} kg·m/s"]}
    # gravitational potential energy
    if ("potential energy" in q or "طاقة وضع" in q) and len(nums)>=3:
        m,g,h=nums[0],nums[1],nums[2]
        return {"topic":"gravitational potential energy","equation":"U = mgh",
                "result":m*g*h,"unit":"J",
                "steps":[f"U = {m} × {g} × {h}",f"U = {m*g*h} J"]}
    # wave speed
    if ("wave speed" in q or "سرعة الموجة" in q) and len(nums)>=2:
        f,lam=nums[0],nums[1]
        return {"topic":"wave speed","equation":"v = fλ","result":f*lam,
                "unit":"m/s","steps":[f"v = {f} × {lam}",f"v = {f*lam} m/s"]}
    # electrical power
    if ("electrical power" in q or "القدرة الكهربائية" in q) and len(nums)>=2:
        v,i=nums[0],nums[1]
        return {"topic":"electrical power","equation":"P = VI","result":v*i,
                "unit":"W","steps":[f"P = {v} × {i}",f"P = {v*i} W"]}
    return None
