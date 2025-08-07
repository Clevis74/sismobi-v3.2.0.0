"""
Routers de Relatórios para API SISMOBI
Autor: E1 Agent  
Data: 2025-01-07
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
from typing import Optional, List
import io

from auth import get_current_user
from models import User
from reports import PDFReportGenerator

router = APIRouter(prefix="/reports", tags=["reports"])

# Instância do gerador de relatórios
report_generator = PDFReportGenerator()

@router.get("/financial", response_class=StreamingResponse)
async def generate_financial_report(
    start_date: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    property_id: Optional[str] = Query(None, description="Filtrar por propriedade"),
    tenant_id: Optional[str] = Query(None, description="Filtrar por inquilino"),
    current_user: User = Depends(get_current_user)
):
    """
    Gera relatório financeiro em PDF
    
    **Filtros disponíveis:**
    - **start_date**: Data de início (formato YYYY-MM-DD)
    - **end_date**: Data de fim (formato YYYY-MM-DD)  
    - **property_id**: UUID da propriedade específica
    - **tenant_id**: UUID do inquilino específico
    
    **Retorna:** PDF com resumo financeiro, transações por categoria e análises
    """
    try:
        # Converter strings para datetime se fornecidas
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Gerar relatório PDF
        pdf_bytes = await report_generator.generate_financial_report(
            start_date=start_dt,
            end_date=end_dt,
            property_id=property_id,
            tenant_id=tenant_id
        )
        
        # Criar filename com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_financeiro_{timestamp}.pdf"
        
        # Retornar como stream
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Formato de data inválido: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")


@router.get("/properties", response_class=StreamingResponse)
async def generate_properties_report(
    status: Optional[str] = Query(None, description="Filtrar por status (available, occupied, maintenance, unavailable)"),
    property_type: Optional[str] = Query(None, description="Filtrar por tipo de propriedade"),
    current_user: User = Depends(get_current_user)
):
    """
    Gera relatório de propriedades em PDF
    
    **Filtros disponíveis:**
    - **status**: Status da propriedade (available, occupied, maintenance, unavailable)
    - **property_type**: Tipo da propriedade (apartment, house, commercial, etc.)
    
    **Retorna:** PDF com resumo de propriedades, estatísticas por status/tipo
    """
    try:
        # Gerar relatório PDF
        pdf_bytes = await report_generator.generate_properties_report(
            status_filter=status,
            property_type=property_type
        )
        
        # Criar filename com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_propriedades_{timestamp}.pdf"
        
        # Retornar como stream
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")


@router.get("/tenants", response_class=StreamingResponse)
async def generate_tenants_report(
    property_id: Optional[str] = Query(None, description="Filtrar por propriedade"),
    status: Optional[str] = Query(None, description="Filtrar por status (active, inactive)"),
    current_user: User = Depends(get_current_user)
):
    """
    Gera relatório de inquilinos em PDF
    
    **Filtros disponíveis:**
    - **property_id**: UUID da propriedade específica
    - **status**: Status do inquilino (active, inactive)
    
    **Retorna:** PDF com resumo de inquilinos, lista detalhada com informações de contato
    """
    try:
        # Gerar relatório PDF
        pdf_bytes = await report_generator.generate_tenants_report(
            property_id=property_id,
            status_filter=status
        )
        
        # Criar filename com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_inquilinos_{timestamp}.pdf"
        
        # Retornar como stream
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")


@router.get("/comprehensive", response_class=StreamingResponse)
async def generate_comprehensive_report(
    start_date: Optional[str] = Query(None, description="Data início para análise financeira (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data fim para análise financeira (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user)
):
    """
    Gera relatório completo do sistema em PDF
    
    **Inclui:**
    - Visão geral do dashboard
    - Resumo financeiro
    - Estatísticas de propriedades
    - Informações de inquilinos
    - Alertas pendentes
    
    **Filtros para análise financeira:**
    - **start_date**: Data de início (formato YYYY-MM-DD)
    - **end_date**: Data de fim (formato YYYY-MM-DD)
    
    **Retorna:** PDF completo com todas as informações do sistema
    """
    try:
        # Converter strings para datetime se fornecidas
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Gerar relatório PDF
        pdf_bytes = await report_generator.generate_comprehensive_report(
            start_date=start_dt,
            end_date=end_dt
        )
        
        # Criar filename com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_completo_sismobi_{timestamp}.pdf"
        
        # Retornar como stream
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Formato de data inválido: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")


@router.get("/quick-financial", response_class=StreamingResponse)
async def generate_quick_financial_report(
    period: str = Query("current_month", description="Período pré-definido (current_month, last_month, current_year, last_30_days)"),
    current_user: User = Depends(get_current_user)
):
    """
    Gera relatório financeiro rápido com períodos pré-definidos
    
    **Períodos disponíveis:**
    - **current_month**: Mês atual
    - **last_month**: Mês anterior
    - **current_year**: Ano atual
    - **last_30_days**: Últimos 30 dias
    - **last_90_days**: Últimos 90 dias
    
    **Retorna:** PDF com análise financeira do período selecionado
    """
    try:
        now = datetime.now()
        
        # Definir datas baseadas no período
        if period == "current_month":
            start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_dt = now
        elif period == "last_month":
            # Primeiro dia do mês passado
            first_last_month = now.replace(day=1) - timedelta(days=1)
            start_dt = first_last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Último dia do mês passado  
            end_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
        elif period == "current_year":
            start_dt = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_dt = now
        elif period == "last_30_days":
            start_dt = now - timedelta(days=30)
            end_dt = now
        elif period == "last_90_days":
            start_dt = now - timedelta(days=90)
            end_dt = now
        else:
            raise HTTPException(status_code=400, detail="Período inválido")
        
        # Gerar relatório PDF
        pdf_bytes = await report_generator.generate_financial_report(
            start_date=start_dt,
            end_date=end_dt
        )
        
        # Criar filename com timestamp e período
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_financeiro_{period}_{timestamp}.pdf"
        
        # Retornar como stream
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")


@router.get("/available-filters")
async def get_available_filters(
    current_user: User = Depends(get_current_user)
):
    """
    Retorna os filtros disponíveis para os relatórios
    
    **Retorna:**
    - Propriedades disponíveis (para filtros por propriedade)
    - Inquilinos disponíveis (para filtros por inquilino)
    - Status disponíveis
    - Tipos de propriedade disponíveis
    """
    try:
        from database import get_collection
        from utils import convert_objectid_to_str
        
        # Buscar propriedades para filtros
        properties_collection = get_collection("properties")
        properties_cursor = properties_collection.find({}, {"id": 1, "address": 1, "type": 1, "status": 1})
        properties = [convert_objectid_to_str(doc) async for doc in properties_cursor]
        
        # Buscar inquilinos para filtros
        tenants_collection = get_collection("tenants")
        tenants_cursor = tenants_collection.find({}, {"id": 1, "name": 1, "email": 1, "status": 1})
        tenants = [convert_objectid_to_str(doc) async for doc in tenants_cursor]
        
        # Status disponíveis
        property_status = ["available", "occupied", "maintenance", "unavailable"]
        tenant_status = ["active", "inactive"]
        
        # Tipos de propriedade únicos
        property_types = list(set([p.get("type", "") for p in properties if p.get("type")]))
        
        return {
            "properties": [
                {"id": p["id"], "address": p.get("address", ""), "type": p.get("type", ""), "status": p.get("status", "")}
                for p in properties
            ],
            "tenants": [
                {"id": t["id"], "name": t.get("name", ""), "email": t.get("email", ""), "status": t.get("status", "")}
                for t in tenants
            ],
            "property_status": property_status,
            "tenant_status": tenant_status,
            "property_types": property_types,
            "quick_periods": [
                {"key": "current_month", "label": "Mês Atual"},
                {"key": "last_month", "label": "Mês Anterior"},
                {"key": "current_year", "label": "Ano Atual"},
                {"key": "last_30_days", "label": "Últimos 30 Dias"},
                {"key": "last_90_days", "label": "Últimos 90 Dias"}
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar filtros disponíveis: {str(e)}")


@router.get("/history")
async def get_reports_history(
    limit: int = Query(20, description="Número máximo de registros"),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna histórico de relatórios gerados (funcionalidade futura)
    
    **Parâmetros:**
    - **limit**: Número máximo de registros a retornar
    
    **Nota:** Esta funcionalidade será implementada para tracking de relatórios gerados
    """
    # Por enquanto, retorna uma mensagem informativa
    # Em uma implementação futura, esto seria conectado a uma collection de histórico
    return {
        "message": "Histórico de relatórios - funcionalidade será implementada",
        "reports": [],
        "total": 0,
        "note": "Para implementar: criar collection 'reports_history' e registrar cada geração"
    }