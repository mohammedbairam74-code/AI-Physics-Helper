import math

def solve_mechanics(problem: str):
    q=problem.lower().replace("×","*")
    # Explicit lightweight calculator for common kinetic-energy / Newton / Ohm examples.
    import re
    nums=[float(x) for x in re.findall(r'(?<![a-z])\d+(?:\.\d+)?',q)]
    if ("kinetic" in q or "طاقة حركية" in q) and len(nums)>=2:
        m,v=nums[0],nums[1]
        e=0.5*m*v*v
        return {
          "type":"kinetic_energy",
          "givens":{"m_kg":m,"v_m_s":v},
          "equation":"K = 1/2 m v^2",
          "result_j":e,
          "steps":[f"K = 1/2 × {m} × ({v})²",f"K = {e} J"]
        }
    if ("ohm" in q or "أوم" in q) and len(nums)>=2:
        v,i=nums[0],nums[1]
        r=v/i if i else None
        return {"type":"ohms_law","givens":{"V":v,"I":i},
                "equation":"R = V / I","result_ohm":r,
                "steps":[f"R = {v} / {i}",f"R = {r} Ω" if r is not None else "I cannot divide by zero."]}
    return None
