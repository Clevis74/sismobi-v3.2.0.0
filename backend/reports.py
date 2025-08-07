"""
Sistema de Geração de Relatórios em PDF para SISMOBI
Autor: E1 Agent
Data: 2025-01-07
"""

import io
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.widgets.markers import makeMarker
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import base64

from database import get_collection
from models import Property, Tenant, Transaction, Alert
from utils import convert_objectid_to_str

class PDFReportGenerator:
    """Gerador de relatórios em PDF para SISMOBI"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Configura estilos personalizados para os relatórios"""
        
        # Estilo para título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),  # Blue-700
            alignment=TA_CENTER,
            spaceAfter=30
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'], 
            fontSize=16,
            textColor=colors.HexColor('#374151'),  # Gray-700
            alignment=TA_LEFT,
            spaceAfter=20,
            spaceBefore=20
        ))
        
        # Estilo para texto de resumo
        self.styles.add(ParagraphStyle(
            name='CustomSummary',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#6b7280'),  # Gray-500
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        # Estilo para valores monetários
        self.styles.add(ParagraphStyle(
            name='MoneyValue',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#059669'),  # Green-600
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))

    async def generate_financial_report(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        property_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> bytes:
        """Gera relatório financeiro em PDF"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        story = []
        
        # Header do relatório
        story.extend(await self._create_header("Relatório Financeiro"))
        story.extend(await self._create_period_info(start_date, end_date))
        
        # Buscar dados das transações
        transactions_data = await self._get_transactions_data(
            start_date, end_date, property_id, tenant_id
        )
        
        # Resumo financeiro
        story.extend(await self._create_financial_summary(transactions_data))
        
        # Detalhamento por categoria
        story.extend(await self._create_transactions_detail(transactions_data))
        
        # Gráfico de receitas vs despesas (se houver dados)
        if transactions_data['transactions']:
            story.extend(await self._create_financial_chart(transactions_data))
        
        # Footer
        story.extend(await self._create_footer())
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    async def generate_properties_report(
        self,
        status_filter: Optional[str] = None,
        property_type: Optional[str] = None
    ) -> bytes:
        """Gera relatório de propriedades em PDF"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        story = []
        
        # Header do relatório
        story.extend(await self._create_header("Relatório de Propriedades"))
        
        # Buscar dados das propriedades
        properties_data = await self._get_properties_data(status_filter, property_type)
        
        # Resumo de propriedades
        story.extend(await self._create_properties_summary(properties_data))
        
        # Lista detalhada de propriedades
        story.extend(await self._create_properties_detail(properties_data))
        
        # Footer
        story.extend(await self._create_footer())
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    async def generate_tenants_report(
        self,
        property_id: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> bytes:
        """Gera relatório de inquilinos em PDF"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        story = []
        
        # Header do relatório
        story.extend(await self._create_header("Relatório de Inquilinos"))
        
        # Buscar dados dos inquilinos
        tenants_data = await self._get_tenants_data(property_id, status_filter)
        
        # Resumo de inquilinos
        story.extend(await self._create_tenants_summary(tenants_data))
        
        # Lista detalhada de inquilinos
        story.extend(await self._create_tenants_detail(tenants_data))
        
        # Footer
        story.extend(await self._create_footer())
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    async def generate_comprehensive_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> bytes:
        """Gera relatório completo do sistema"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        story = []
        
        # Header do relatório
        story.extend(await self._create_header("Relatório Completo SISMOBI"))
        story.extend(await self._create_period_info(start_date, end_date))
        
        # Dashboard summary
        dashboard_data = await self._get_dashboard_summary()
        story.extend(await self._create_dashboard_summary(dashboard_data))
        
        # Resumo financeiro
        transactions_data = await self._get_transactions_data(start_date, end_date)
        story.extend(await self._create_financial_summary(transactions_data))
        
        # Resumo de propriedades
        properties_data = await self._get_properties_data()
        story.extend(await self._create_properties_summary(properties_data))
        
        # Resumo de inquilinos
        tenants_data = await self._get_tenants_data()
        story.extend(await self._create_tenants_summary(tenants_data))
        
        # Alertas pendentes
        alerts_data = await self._get_alerts_data()
        story.extend(await self._create_alerts_summary(alerts_data))
        
        # Footer
        story.extend(await self._create_footer())
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    # Métodos auxiliares para criação de seções do PDF

    async def _create_header(self, title: str) -> List:
        """Cria header do relatório"""
        elements = []
        
        # Logo e título (simulado)
        elements.append(Paragraph("🏢 SISMOBI", self.styles['CustomTitle']))
        elements.append(Paragraph(title, self.styles['CustomSubtitle']))
        elements.append(Paragraph(
            f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
            self.styles['CustomSummary']
        ))
        elements.append(Spacer(1, 20))
        
        return elements

    async def _create_period_info(
        self, 
        start_date: Optional[datetime], 
        end_date: Optional[datetime]
    ) -> List:
        """Cria informações do período"""
        elements = []
        
        if start_date and end_date:
            period_text = f"Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}"
        elif start_date:
            period_text = f"A partir de: {start_date.strftime('%d/%m/%Y')}"
        elif end_date:
            period_text = f"Até: {end_date.strftime('%d/%m/%Y')}"
        else:
            period_text = "Período: Todos os dados disponíveis"
            
        elements.append(Paragraph(period_text, self.styles['CustomSummary']))
        elements.append(Spacer(1, 15))
        
        return elements

    async def _create_footer(self) -> List:
        """Cria footer do relatório"""
        elements = []
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(
            f"Relatório gerado pelo SISMOBI v3.2.0 - © 2025",
            self.styles['CustomSummary']
        ))
        return elements

    # Métodos para busca de dados

    async def _get_transactions_data(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        property_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Busca dados de transações com filtros"""
        
        collection = get_collection("transactions")
        query = {}
        
        # Filtros de data
        if start_date or end_date:
            query["date"] = {}
            if start_date:
                query["date"]["$gte"] = start_date
            if end_date:
                query["date"]["$lte"] = end_date
                
        # Filtros por propriedade/inquilino
        if property_id:
            query["property_id"] = property_id
        if tenant_id:
            query["tenant_id"] = tenant_id
            
        cursor = collection.find(query).sort("date", -1)
        transactions = [convert_objectid_to_str(doc) async for doc in cursor]
        
        # Calcular resumo financeiro
        total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
        total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
        net_result = total_income - total_expense
        
        # Agrupar por categoria
        categories = {}
        for transaction in transactions:
            category = transaction.get("category", "Outros")
            if category not in categories:
                categories[category] = {"income": 0, "expense": 0}
            categories[category][transaction["type"]] += transaction["amount"]
        
        return {
            "transactions": transactions,
            "total_income": total_income,
            "total_expense": total_expense,
            "net_result": net_result,
            "categories": categories,
            "count": len(transactions)
        }

    async def _get_properties_data(
        self,
        status_filter: Optional[str] = None,
        property_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Busca dados de propriedades com filtros"""
        
        collection = get_collection("properties")
        query = {}
        
        if status_filter:
            query["status"] = status_filter
        if property_type:
            query["type"] = property_type
            
        cursor = collection.find(query).sort("created_at", -1)
        properties = [convert_objectid_to_str(doc) async for doc in cursor]
        
        # Estatísticas
        status_count = {}
        type_count = {}
        total_rent = 0
        
        for prop in properties:
            # Count by status
            status = prop.get("status", "unknown")
            status_count[status] = status_count.get(status, 0) + 1
            
            # Count by type  
            prop_type = prop.get("type", "unknown")
            type_count[prop_type] = type_count.get(prop_type, 0) + 1
            
            # Total rent
            if prop.get("rent"):
                total_rent += prop["rent"]
        
        return {
            "properties": properties,
            "count": len(properties),
            "status_count": status_count,
            "type_count": type_count,
            "total_rent": total_rent
        }

    async def _get_tenants_data(
        self,
        property_id: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Busca dados de inquilinos com filtros"""
        
        collection = get_collection("tenants")
        query = {}
        
        if property_id:
            query["property_id"] = property_id
        if status_filter:
            query["status"] = status_filter
            
        cursor = collection.find(query).sort("created_at", -1)
        tenants = [convert_objectid_to_str(doc) async for doc in cursor]
        
        # Estatísticas
        active_count = len([t for t in tenants if t.get("status") == "active"])
        inactive_count = len(tenants) - active_count
        
        return {
            "tenants": tenants,
            "count": len(tenants),
            "active_count": active_count,
            "inactive_count": inactive_count
        }

    async def _get_dashboard_summary(self) -> Dict[str, Any]:
        """Busca dados do dashboard"""
        
        # Buscar todas as collections
        properties = get_collection("properties")
        tenants = get_collection("tenants")
        transactions = get_collection("transactions")
        alerts = get_collection("alerts")
        
        # Contar totais
        total_properties = await properties.count_documents({})
        total_tenants = await tenants.count_documents({})
        occupied_properties = await properties.count_documents({"status": "occupied"})
        vacant_properties = total_properties - occupied_properties
        
        # Transações do mês atual
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_income = await transactions.aggregate([
            {"$match": {"type": "income", "date": {"$gte": start_of_month}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(length=1)
        
        monthly_expenses = await transactions.aggregate([
            {"$match": {"type": "expense", "date": {"$gte": start_of_month}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(length=1)
        
        monthly_income = monthly_income[0]["total"] if monthly_income else 0
        monthly_expenses = monthly_expenses[0]["total"] if monthly_expenses else 0
        
        # Alertas pendentes
        pending_alerts = await alerts.count_documents({"resolved": False})
        
        return {
            "total_properties": total_properties,
            "total_tenants": total_tenants,
            "occupied_properties": occupied_properties,
            "vacant_properties": vacant_properties,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "net_result": monthly_income - monthly_expenses,
            "pending_alerts": pending_alerts
        }

    async def _get_alerts_data(self) -> Dict[str, Any]:
        """Busca dados de alertas"""
        
        collection = get_collection("alerts")
        cursor = collection.find({"resolved": False}).sort("priority", 1).sort("created_at", -1)
        alerts = [convert_objectid_to_str(doc) async for doc in cursor]
        
        # Contar por prioridade
        priority_count = {}
        for alert in alerts:
            priority = alert.get("priority", "medium")
            priority_count[priority] = priority_count.get(priority, 0) + 1
        
        return {
            "alerts": alerts,
            "count": len(alerts),
            "priority_count": priority_count
        }

    # Métodos para criação de seções específicas

    async def _create_financial_summary(self, data: Dict[str, Any]) -> List:
        """Cria resumo financeiro"""
        elements = []
        
        elements.append(Paragraph("💰 Resumo Financeiro", self.styles['CustomSubtitle']))
        
        # Tabela de resumo
        table_data = [
            ['Item', 'Valor'],
            ['Total de Receitas', f"R$ {data['total_income']:,.2f}"],
            ['Total de Despesas', f"R$ {data['total_expense']:,.2f}"],
            ['Resultado Líquido', f"R$ {data['net_result']:,.2f}"],
            ['Total de Transações', f"{data['count']} transações"]
        ]
        
        table = Table(table_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements

    async def _create_transactions_detail(self, data: Dict[str, Any]) -> List:
        """Cria detalhamento de transações"""
        elements = []
        
        if not data['transactions']:
            elements.append(Paragraph("Nenhuma transação encontrada no período.", self.styles['Normal']))
            return elements
        
        elements.append(Paragraph("📊 Detalhamento por Categoria", self.styles['CustomSubtitle']))
        
        # Tabela por categoria
        table_data = [['Categoria', 'Receitas', 'Despesas', 'Saldo']]
        
        for category, amounts in data['categories'].items():
            saldo = amounts['income'] - amounts['expense']
            table_data.append([
                category,
                f"R$ {amounts['income']:,.2f}",
                f"R$ {amounts['expense']:,.2f}",
                f"R$ {saldo:,.2f}"
            ])
        
        table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements

    async def _create_financial_chart(self, data: Dict[str, Any]) -> List:
        """Cria gráfico financeiro"""
        elements = []
        
        # Nota: Em um ambiente real, aqui seria criado um gráfico com matplotlib
        # Por simplicidade, vamos adicionar apenas uma representação textual
        elements.append(Paragraph("📈 Análise Visual", self.styles['CustomSubtitle']))
        elements.append(Paragraph(
            f"Receitas representam {(data['total_income']/(data['total_income']+data['total_expense'])*100):,.1f}% do total de movimentações." if data['total_income']+data['total_expense'] > 0 else "Sem movimentações no período.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 20))
        
        return elements

    async def _create_properties_summary(self, data: Dict[str, Any]) -> List:
        """Cria resumo de propriedades"""
        elements = []
        
        elements.append(Paragraph("🏠 Resumo de Propriedades", self.styles['CustomSubtitle']))
        
        # Tabela de resumo
        table_data = [
            ['Item', 'Quantidade'],
            ['Total de Propriedades', str(data['count'])],
            ['Valor Total de Aluguel', f"R$ {data['total_rent']:,.2f}"]
        ]
        
        # Adicionar estatísticas por status
        for status, count in data['status_count'].items():
            status_name = {
                'available': 'Disponíveis',
                'occupied': 'Ocupadas', 
                'maintenance': 'Em Manutenção',
                'unavailable': 'Indisponíveis'
            }.get(status, status.title())
            table_data.append([status_name, str(count)])
        
        table = Table(table_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements

    async def _create_properties_detail(self, data: Dict[str, Any]) -> List:
        """Cria detalhamento de propriedades"""
        elements = []
        
        if not data['properties']:
            elements.append(Paragraph("Nenhuma propriedade encontrada.", self.styles['Normal']))
            return elements
        
        elements.append(Paragraph("🏘️ Lista de Propriedades", self.styles['CustomSubtitle']))
        
        # Tabela de propriedades (limitada às primeiras 10 para não sobrecarregar)
        table_data = [['Endereço', 'Tipo', 'Status', 'Aluguel']]
        
        for prop in data['properties'][:10]:  # Limitar a 10
            table_data.append([
                prop.get('address', 'N/A')[:30],  # Limitar tamanho
                prop.get('type', 'N/A'),
                {
                    'available': 'Disponível',
                    'occupied': 'Ocupada',
                    'maintenance': 'Manutenção',
                    'unavailable': 'Indisponível'
                }.get(prop.get('status'), 'N/A'),
                f"R$ {prop.get('rent', 0):,.2f}"
            ])
        
        if len(data['properties']) > 10:
            table_data.append([f"... e mais {len(data['properties']) - 10} propriedades", '', '', ''])
        
        table = Table(table_data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 1.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements

    async def _create_tenants_summary(self, data: Dict[str, Any]) -> List:
        """Cria resumo de inquilinos"""
        elements = []
        
        elements.append(Paragraph("👥 Resumo de Inquilinos", self.styles['CustomSubtitle']))
        
        # Tabela de resumo
        table_data = [
            ['Item', 'Quantidade'],
            ['Total de Inquilinos', str(data['count'])],
            ['Inquilinos Ativos', str(data['active_count'])],
            ['Inquilinos Inativos', str(data['inactive_count'])]
        ]
        
        table = Table(table_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements

    async def _create_tenants_detail(self, data: Dict[str, Any]) -> List:
        """Cria detalhamento de inquilinos"""
        elements = []
        
        if not data['tenants']:
            elements.append(Paragraph("Nenhum inquilino encontrado.", self.styles['Normal']))
            return elements
        
        elements.append(Paragraph("👨‍👩‍👧‍👦 Lista de Inquilinos", self.styles['CustomSubtitle']))
        
        # Tabela de inquilinos (limitada às primeiros 10)
        table_data = [['Nome', 'Email', 'Telefone', 'Status']]
        
        for tenant in data['tenants'][:10]:  # Limitar a 10
            table_data.append([
                tenant.get('name', 'N/A')[:20],  # Limitar tamanho
                tenant.get('email', 'N/A')[:25],
                tenant.get('phone', 'N/A'),
                'Ativo' if tenant.get('status') == 'active' else 'Inativo'
            ])
        
        if len(data['tenants']) > 10:
            table_data.append([f"... e mais {len(data['tenants']) - 10} inquilinos", '', '', ''])
        
        table = Table(table_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements

    async def _create_dashboard_summary(self, data: Dict[str, Any]) -> List:
        """Cria resumo do dashboard"""
        elements = []
        
        elements.append(Paragraph("📊 Visão Geral do Sistema", self.styles['CustomSubtitle']))
        
        # Tabela de resumo geral
        table_data = [
            ['Métrica', 'Valor'],
            ['Total de Propriedades', str(data['total_properties'])],
            ['Propriedades Ocupadas', str(data['occupied_properties'])],
            ['Propriedades Vagas', str(data['vacant_properties'])],
            ['Total de Inquilinos', str(data['total_tenants'])],
            ['Receita Mensal', f"R$ {data['monthly_income']:,.2f}"],
            ['Despesas Mensais', f"R$ {data['monthly_expenses']:,.2f}"],
            ['Resultado Líquido', f"R$ {data['net_result']:,.2f}"],
            ['Alertas Pendentes', str(data['pending_alerts'])]
        ]
        
        table = Table(table_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements

    async def _create_alerts_summary(self, data: Dict[str, Any]) -> List:
        """Cria resumo de alertas"""
        elements = []
        
        elements.append(Paragraph("⚠️ Alertas Pendentes", self.styles['CustomSubtitle']))
        
        if not data['alerts']:
            elements.append(Paragraph("🎉 Não há alertas pendentes!", self.styles['Normal']))
            return elements
        
        # Tabela de alertas por prioridade
        table_data = [['Prioridade', 'Quantidade']]
        
        priority_names = {
            'critical': 'Crítica',
            'high': 'Alta',
            'medium': 'Média', 
            'low': 'Baixa'
        }
        
        for priority, count in data['priority_count'].items():
            table_data.append([
                priority_names.get(priority, priority.title()),
                str(count)
            ])
        
        table = Table(table_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),  # Red for alerts
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef2f2')),  # Light red
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements