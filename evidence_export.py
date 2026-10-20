"""Export model-agnostic probability-scale Shapley evidence for the browser workbench.
Use all feature attributions, not only the top reasons. See docs/IMPORT_FORMAT.md.
"""
from pathlib import Path
import json

def export_explanations(path, *, model_id, outcome, features, applications, title='Explanation evidence'):
    """features: [{id,label,group?}]; applications: [{id,score,shapley:[{id,reference,baseline,values:{feature:phi}}]}].
    Optional local_approximations carry coefficients and explicitly labeled fidelity evidence.
    This function packages evidence; it does not validate the model or authenticate its provenance.
    """
    pack={'schema_version':'credit-explanation-evidence/v1','title':title,
          'model':{'id':model_id,'output':outcome,'score_scale':'probability'},
          'features':features,'applications':applications}
    Path(path).write_text(json.dumps(pack,indent=2,allow_nan=False))
    return pack
