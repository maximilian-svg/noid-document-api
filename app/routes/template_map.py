from fastapi import APIRouter

router = APIRouter()

@router.get("")
def get_template_map():
    return {
        "Bas": "NOID_Rapportmall_Bas_Maskinfyllbar_v13.docx",
        "Fokus": "NOID_Rapportmall_Fokus_Maskinfyllbar_v12.docx",
        "Optimal": "NOID_Rapportmall_Optimal_Maskinfyllbar_v12.docx",
        "Återbesök": "NOID_Rapportmall_Aterbesok_Maskinfyllbar_v12.docx"
    }