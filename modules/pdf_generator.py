from fpdf import FPDF
from datetime import datetime
import pandas as pd
from .utils import format_currency
from .config import FORMAS_PAGAMENTO_VALIDAS, INVALID_CLIENTS

def create_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=10)

    left_margin = 10
    right_margin = 10
    pdf.set_left_margin(left_margin)
    pdf.set_right_margin(right_margin)
    page_width = pdf.w - left_margin - right_margin

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(page_width, 10, txt="BNS - RELATÓRIO DE ANÁLISES FINANCEIRAS", ln=1, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", size=10)
    pdf.cell(page_width, 10, txt=f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=1, align='R')
    pdf.ln(10)

    completed_services = data[data['Realizado']]
    not_completed = data[(data['Realizado'] == False) & (data['Cliente'].notna())]

    metrics = [
        ("Atendimentos Realizados", len(completed_services)),
        ("Atendimentos Não Realizados", len(not_completed)),
        ("Total em Serviços", format_currency(completed_services['Serviço'].sum())),
        ("Total em Gorjetas", format_currency(completed_services['Gorjeta'].sum())),
        ("Total de Entrada", format_currency(completed_services['Lucro Empresa'].sum()))
    ]

    for metric, value in metrics:
        pdf.cell(page_width / 2, 10, txt=f"{metric}:", ln=0)
        pdf.cell(page_width / 2, 10, txt=str(value), ln=1)

    pdf.ln(10)

    # Resumo por Técnico
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(page_width, 10, txt="Resumo por Técnico", ln=1)

    tech_summary = completed_services.groupby(['Nome', 'Categoria']).agg({
        'Serviço': 'sum',
        'Gorjeta': 'sum',
        'Pagamento Tecnico': 'sum',
        'Lucro Empresa': 'sum',
        'Cliente': 'count'
    }).reset_index()

    tech_summary.columns = ['Técnico', 'Categoria', 'Total Serviços', 'Total Gorjetas',
                             'Total Pagamento', 'Lucro Empresa', 'Atendimentos']

    pdf.set_font("Arial", size=8)
    col_widths = [30, 25, 25, 25, 25, 25]

    headers = ["Técnico", "Categoria", "Serviços", "Gorjetas", "Pagamento", "Lucro"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, txt=header, border=1, align='C')
    pdf.ln()

    for _, row in tech_summary.iterrows():
        pdf.cell(col_widths[0], 10, txt=str(row['Técnico'])[:15], border=1)
        pdf.cell(col_widths[1], 10, txt=str(row['Categoria'])[:10], border=1)
        pdf.cell(col_widths[2], 10, txt=format_currency(row['Total Serviços']), border=1, align='R')
        pdf.cell(col_widths[3], 10, txt=format_currency(row['Total Gorjetas']), border=1, align='R')
        pdf.cell(col_widths[4], 10, txt=format_currency(row['Total Pagamento']), border=1, align='R')
        pdf.cell(col_widths[5], 10, txt=format_currency(row['Lucro Empresa']), border=1, align='R')
        pdf.ln()

    pdf.ln(10)

    # Seção 2: Resumo por Técnico
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(page_width, 10, txt="2. Resumo por Técnico", ln=1)

    tech_summary = completed_services.groupby(['Nome', 'Categoria']).agg({
        'Serviço': 'sum',
        'Gorjeta': 'sum',
        'Pagamento Tecnico': 'sum',
        'Lucro Empresa': 'sum',
        'Cliente': 'count'
    }).reset_index()

    tech_summary.columns = ['Técnico', 'Categoria', 'Total Serviços', 'Total Gorjetas',
                            'Total Pagamento', 'Lucro Empresa', 'Atendimentos']

    pdf.set_font("Arial", size=8)
    col_widths = [30, 25, 25, 25, 25, 25]

    headers = ["Técnico", "Categoria", "Serviços", "Gorjetas", "Pagamento", "Lucro"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, txt=header, border=1, align='C')
    pdf.ln()

    for _, row in tech_summary.iterrows():
        tech_name = str(row['Técnico'])[:15] + '...' if len(str(row['Técnico'])) > 15 else str(row['Técnico'])
        pdf.cell(col_widths[0], 10, txt=tech_name, border=1)
        pdf.cell(col_widths[1], 10, txt=str(row['Categoria'])[:10], border=1)
        pdf.cell(col_widths[2], 10, txt=format_currency(row['Total Serviços']), border=1, align='R')
        pdf.cell(col_widths[3], 10, txt=format_currency(row['Total Gorjetas']), border=1, align='R')
        pdf.cell(col_widths[4], 10, txt=format_currency(row['Total Pagamento']), border=1, align='R')
        pdf.cell(col_widths[5], 10, txt=format_currency(row['Lucro Empresa']), border=1, align='R')
        pdf.ln()

    pdf.ln(10)

    # Seção 3: Métodos de Pagamento
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(page_width, 10, txt="3. Métodos de Pagamento", ln=1)
    pdf.set_font("Arial", size=10)

    valid_payments = completed_services[completed_services['Pagamento'].isin(FORMAS_PAGAMENTO_VALIDAS)]

    if not valid_payments.empty:
        payment_methods = valid_payments.groupby('Pagamento').agg({
            'Serviço': ['sum', 'count'],
            'Gorjeta': 'sum',
            'Lucro Empresa': 'sum'
        }).reset_index()

        payment_methods.columns = ['Método', 'Total Serviços', 'Qtd Usos', 'Total Gorjetas', 'Lucro Empresa']
        payment_methods['Total Geral'] = payment_methods['Total Serviços'] + payment_methods['Total Gorjetas']

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(page_width, 10, txt="Resumo por Método de Pagamento:", ln=1)
        pdf.set_font("Arial", size=8)

        headers = ["Método", "Usos", "Serviços", "Gorjetas", "Total", "Lucro"]
        col_widths_payments = [30, 20, 25, 25, 25, 25]

        for i, header in enumerate(headers):
            pdf.cell(col_widths_payments[i], 10, txt=header, border=1, align='C')
        pdf.ln()

        for _, row in payment_methods.iterrows():
            pdf.cell(col_widths_payments[0], 10, txt=str(row['Método'])[:12], border=1)
            pdf.cell(col_widths_payments[1], 10, txt=str(row['Qtd Usos']), border=1, align='C')
            pdf.cell(col_widths_payments[2], 10, txt=format_currency(row['Total Serviços']), border=1, align='R')
            pdf.cell(col_widths_payments[3], 10, txt=format_currency(row['Total Gorjetas']), border=1, align='R')
            pdf.cell(col_widths_payments[4], 10, txt=format_currency(row['Total Geral']), border=1, align='R')
            pdf.cell(col_widths_payments[5], 10, txt=format_currency(row['Lucro Empresa']), border=1, align='R')
            pdf.ln()

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(page_width, 10, txt="Distribuição por Método de Pagamento:", ln=1)
        pdf.set_font("Arial", size=10)

        total_usos = payment_methods['Qtd Usos'].sum()
        for _, row in payment_methods.iterrows():
            percent = (row['Qtd Usos'] / total_usos * 100)
            pdf.cell(page_width / 2, 10, txt=f"{row['Método']}:", ln=0)
            pdf.cell(page_width / 2, 10, txt=f"{percent:.1f}% ({row['Qtd Usos']} usos)", ln=1)

    pdf.ln(10)

    # Seção 4: Atendimentos por Dia da Semana
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(page_width, 10, txt="4. Atendimentos por Dia da Semana", ln=1)
    pdf.set_font("Arial", size=10)

    day_summary = completed_services.groupby('Dia').agg({
        'Serviço': ['count', 'sum'],
        'Gorjeta': 'sum',
        'Lucro Empresa': 'sum'
    }).reset_index()

    day_summary.columns = ['Dia', 'Atendimentos', 'Total Serviços', 'Total Gorjetas', 'Lucro Empresa']
    day_summary['Dia'] = pd.Categorical(day_summary['Dia'],
                                       categories=['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'],
                                       ordered=True)
    day_summary = day_summary.sort_values('Dia')

    col_widths_days = [30, 25, 30, 30, 30]
    headers = ["Dia", "Atend.", "Serviços", "Gorjetas", "Lucro"]

    pdf.set_font("Arial", size=8)
    for i, header in enumerate(headers):
        pdf.cell(col_widths_days[i], 10, txt=header, border=1, align='C')
    pdf.ln()

    for _, row in day_summary.iterrows():
        pdf.cell(col_widths_days[0], 10, txt=str(row['Dia']), border=1)
        pdf.cell(col_widths_days[1], 10, txt=str(row['Atendimentos']), border=1, align='C')
        pdf.cell(col_widths_days[2], 10, txt=format_currency(row['Total Serviços']), border=1, align='R')
        pdf.cell(col_widths_days[3], 10, txt=format_currency(row['Total Gorjetas']), border=1, align='R')
        pdf.cell(col_widths_days[4], 10, txt=format_currency(row['Lucro Empresa']), border=1, align='R')
        pdf.ln()

    pdf.ln(10)

    # Seção 5: Atendimentos Não Realizados
    if len(not_completed) > 0:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(page_width, 10, txt="5. Atendimentos Não Realizados", ln=1)
        pdf.set_font("Arial", size=10)

        pdf.cell(page_width, 10, txt=f"Total de atendimentos não realizados: {len(not_completed)}", ln=1)

        pdf.set_font("Arial", size=8)
        for idx, row in not_completed.head(10).iterrows():
            pdf.cell(page_width, 10,
                     txt=f"- {row['Nome']} | {row['Dia']} {row['Data'].strftime('%d/%m')} | {row['Cliente']}",
                     ln=1)

    return pdf


def create_tech_payment_receipt(tech_data, tech_name, week):
    """Cria um PDF com o recibo de pagamento detalhado para o técnico com papel timbrado"""
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    left_margin = 15
    right_margin = 15
    pdf.set_left_margin(left_margin)
    pdf.set_right_margin(right_margin)
    page_width = pdf.w - left_margin - right_margin
    page_height = pdf.h

    min_date = tech_data['Data'].min().strftime('%m/%d/%y')
    max_date = tech_data['Data'].max().strftime('%m/%d/%y')
    date_range = f"{min_date} to {max_date}"

    pdf.set_font("Arial", 'B', 18)
    pdf.cell(page_width, 10, txt="TECHNICIAN PAYMENT RECEIPT", ln=1, align='C')
    pdf.ln(9)

    pdf.set_font("Arial", size=10)
    pdf.cell(page_width, 8, txt=f"Technician: {tech_name}", ln=1)
    pdf.cell(page_width, 8, txt=f"Reference: {date_range}", ln=1)
    pdf.cell(page_width, 8, txt=f"Date of issue: {datetime.now().strftime('%m/%d/%Y')}", ln=1)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(page_width, 10, txt="SUMMARY OF SERVICES", ln=1)
    pdf.set_font("Arial", size=10)

    total_services = tech_data['Serviço'].sum()
    total_tips = tech_data['Gorjeta'].sum()
    total_payment = tech_data['Pagamento Tecnico'].sum()

    def format_value(value):
        return f"${value:,.2f}" if isinstance(value, (int, float)) else str(value)

    col_widths = [page_width / 2, page_width / 2]

    pdf.cell(col_widths[0], 10, txt="Total Schedules:", border='B', ln=0)
    pdf.cell(col_widths[1], 10, txt=str(len(tech_data)), border='B', ln=1, align='R')

    pdf.cell(col_widths[0], 10, txt="Total in Services:", border='B', ln=0)
    pdf.cell(col_widths[1], 10, txt=format_value(total_services), border='B', ln=1, align='R')

    pdf.cell(col_widths[0], 10, txt="Total in Tips:", border='B', ln=0)
    pdf.cell(col_widths[1], 10, txt=format_value(total_tips), border='B', ln=1, align='R')

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(col_widths[0], 10, txt="Total Payment", border='B', ln=0)
    pdf.cell(col_widths[1], 10, txt=format_value(total_payment), border='B', ln=1, align='R')
    pdf.set_font("Arial", size=10)

    pdf.ln(15)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(page_width, 10, txt="DETAILS BY DAY", ln=1)
    pdf.set_font("Arial", size=8)

    day_details = tech_data.groupby('Dia').agg({
        'Serviço': 'sum',
        'Gorjeta': 'sum',
        'Cliente': 'count',
        'Pagamento': lambda x: ', '.join([str(p) for p in x.unique() if pd.notna(p)])
    }).reset_index()

    day_mapping = {
        'Domingo': 'Sun',
        'Segunda': 'Mon',
        'Terça': 'Tue',
        'Quarta': 'Wed',
        'Quinta': 'Thu',
        'Sexta': 'Fri',
        'Sábado': 'Sat'
    }
    day_details['Dia'] = day_details['Dia'].map(day_mapping)

    day_order = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    day_details['Dia'] = pd.Categorical(day_details['Dia'], categories=day_order, ordered=True)
    day_details = day_details.sort_values('Dia')

    col_widths = [46, 46, 47, 46]
    headers = ["Day", "Showed", "Services", "Tips"]

    pdf.set_font("Arial", 'B', 7)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 6, txt=header, border=1, align='C')
    pdf.ln()

    pdf.set_font("Arial", size=7)
    for _, row in day_details.iterrows():
        pdf.cell(col_widths[0], 6, txt=str(row['Dia']), border=1)
        pdf.cell(col_widths[1], 6, txt=str(row['Cliente']), border=1, align='C')
        pdf.cell(col_widths[2], 6, txt=format_value(row['Serviço']), border=1, align='R')
        pdf.cell(col_widths[3], 6, txt=format_value(row['Gorjeta']), border=1, align='R')
        pdf.ln()

    pdf.ln(10)

    if pdf.get_y() < page_height - 50:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(page_width, 10, txt="SERVICE DETAILS", ln=1)
        pdf.set_font("Arial", size=7)

        tech_data_sorted = tech_data.sort_values(['Data', 'Dia'])

        col_widths_detailed = [25, 25, 60, 25, 25, 25]
        headers_detailed = ["Date", "Day", "Customer", "Service", "Tips", "Payment"]

        pdf.set_font("Arial", 'B', 8)
        for i, header in enumerate(headers_detailed):
            pdf.cell(col_widths_detailed[i], 6, txt=header, border=1, align='C')
        pdf.ln()

        pdf.set_font("Arial", size=7)
        for _, row in tech_data_sorted.iterrows():
            if pdf.get_y() > page_height - 20:
                pdf.add_page()
                pdf.set_y(30)
                pdf.set_font("Arial", 'B', 8)
                for i, header in enumerate(headers_detailed):
                    pdf.cell(col_widths_detailed[i], 6, txt=header, border=1, align='C')
                pdf.ln()
                pdf.set_font("Arial", size=7)

            pdf.cell(col_widths_detailed[0], 6, txt=row['Data'].strftime('%d/%m'), border=1)
            day_english = day_mapping.get(row['Dia'], row['Dia'])
            pdf.cell(col_widths_detailed[1], 6, txt=day_english, border=1)
            client_name = str(row['Cliente'])[:20] + '...' if len(str(row['Cliente'])) > 20 else str(row['Cliente'])
            pdf.cell(col_widths_detailed[2], 6, txt=client_name, border=1)
            pdf.cell(col_widths_detailed[3], 6, txt=format_value(row['Serviço']), border=1, align='R')
            pdf.cell(col_widths_detailed[4], 6, txt=format_value(row['Gorjeta']), border=1, align='R')
            payment = str(row['Pagamento']) if pd.notna(row['Pagamento']) else "-"
            pdf.cell(col_widths_detailed[5], 6, txt=payment[:12], border=1)
            pdf.ln()

    pdf.set_font("Arial", size=8)
    pdf.cell(page_width, 5, txt="BRIGHT N SHINE PET DENTAL LLC", ln=1, align='C')
    pdf.cell(page_width, 5, txt="(407)259-7897", ln=1, align='C')

    return pdf

def create_technician_of_the_week_receipt(tech_data, tech_name, week):
    """Cria um recibo personalizado para o 'Technician of the Week' sem preenchimento de fundo."""
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    left_margin = 15
    right_margin = 15
    pdf.set_left_margin(left_margin)
    pdf.set_right_margin(right_margin)
    page_width = pdf.w - left_margin - right_margin
    page_height = pdf.h

    min_date = tech_data['Data'].min().strftime('%m/%d/%y')
    max_date = tech_data['Data'].max().strftime('%m/%d/%y')
    date_range = f"{min_date} to {max_date}"

    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(page_width, 10, txt="You have performed many services and have been considered the:", ln=1, align='C')

    # Cabeçalho
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(235, 146, 30)
    pdf.cell(page_width, 15, txt="THE TECHNICIAN OF THE WEEK", ln=1, align='C')

    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(page_width, 10, txt="Bright N Shine congratulates you for your outstanding performance!", ln=1, align='C')
    pdf.ln(5)

    # Dados principais
    pdf.set_font("Arial", '', 11)
    pdf.cell(page_width, 8, txt=f"Technician: {tech_name}", ln=1)
    pdf.cell(page_width, 8, txt=f"Reference: {date_range}", ln=1)
    pdf.cell(page_width, 8, txt=f"Date of issue: {datetime.now().strftime('%m/%d/%Y')}", ln=1)
    pdf.ln(8)

    # Resumo
    total_services = tech_data['Serviço'].sum()
    total_tips = tech_data['Gorjeta'].sum()
    total_payment = tech_data['Pagamento Tecnico'].sum()

    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(page_width, 10, txt="Summary of this Great Week", ln=1, align='C')

    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(page_width / 2, 8, txt="Total Appointments:", ln=0)
    pdf.cell(page_width / 2, 8, txt=str(len(tech_data)), ln=1, align='R')

    pdf.cell(page_width / 2, 8, txt="Total Services:", ln=0)
    pdf.cell(page_width / 2, 8, txt=f"${total_services:,.2f}", ln=1, align='R')

    pdf.cell(page_width / 2, 8, txt="Total Tips:", ln=0)
    pdf.cell(page_width / 2, 8, txt=f"${total_tips:,.2f}", ln=1, align='R')

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(page_width / 2, 8, txt="Total Payment:", ln=0)
    pdf.cell(page_width / 2, 8, txt=f"${total_payment:,.2f}", ln=1, align='R')

    pdf.ln(10)

    # Detalhes por dia
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(page_width, 8, txt="Details by Day", ln=1)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=9)

    day_details = tech_data.groupby('Dia').agg({
        'Serviço': 'sum',
        'Gorjeta': 'sum',
        'Cliente': 'count'
    }).reset_index()

    day_mapping = {
        'Domingo': 'Sun',
        'Segunda': 'Mon',
        'Terça': 'Tue',
        'Quarta': 'Wed',
        'Quinta': 'Thu',
        'Sexta': 'Fri',
        'Sábado': 'Sat'
    }
    day_details['Dia'] = day_details['Dia'].map(day_mapping)

    day_order = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    day_details['Dia'] = pd.Categorical(day_details['Dia'], categories=day_order, ordered=True)
    day_details = day_details.sort_values('Dia')

    headers = ["Day", "Appointments", "Services", "Tips"]
    col_widths = [40, 40, 55, 55]

    pdf.set_font("Arial", 'B', 9)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, txt=header, border=1, align='C')
    pdf.ln()

    pdf.set_font("Arial", size=9)
    for _, row in day_details.iterrows():
        pdf.cell(col_widths[0], 8, txt=str(row['Dia']), border=1)
        pdf.cell(col_widths[1], 8, txt=str(row['Cliente']), border=1, align='C')
        pdf.cell(col_widths[2], 8, txt=f"${row['Serviço']:,.2f}", border=1, align='R')
        pdf.cell(col_widths[3], 8, txt=f"${row['Gorjeta']:,.2f}", border=1, align='R')
        pdf.ln()

    pdf.ln(10)

    # SERVICE DETAILS
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(page_width, 8, txt="Service Details", ln=1)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=8)

    col_widths_detailed = [25, 25, 60, 25, 25, 25]
    headers_detailed = ["Date", "Day", "Customer", "Service", "Tips", "Payment"]

    pdf.set_font("Arial", 'B', 8)
    for i, header in enumerate(headers_detailed):
        pdf.cell(col_widths_detailed[i], 6, txt=header, border=1, align='C')
    pdf.ln()

    pdf.set_font("Arial", size=7)
    tech_data_sorted = tech_data.sort_values(['Data', 'Dia'])

    for _, row in tech_data_sorted.iterrows():
        if pdf.get_y() > page_height - 20:
            pdf.add_page()
            pdf.set_y(30)
            pdf.set_font("Arial", 'B', 8)
            for i, header in enumerate(headers_detailed):
                pdf.cell(col_widths_detailed[i], 6, txt=header, border=1, align='C')
            pdf.ln()
            pdf.set_font("Arial", size=7)

        pdf.cell(col_widths_detailed[0], 6, txt=row['Data'].strftime('%d/%m'), border=1)
        pdf.cell(col_widths_detailed[1], 6, txt=day_mapping.get(row['Dia'], row['Dia']), border=1)
        client_name = str(row['Cliente'])[:20] + '...' if len(str(row['Cliente'])) > 20 else str(row['Cliente'])
        pdf.cell(col_widths_detailed[2], 6, txt=client_name, border=1)
        pdf.cell(col_widths_detailed[3], 6, txt=f"${row['Serviço']:,.2f}", border=1, align='R')
        pdf.cell(col_widths_detailed[4], 6, txt=f"${row['Gorjeta']:,.2f}", border=1, align='R')
        payment = str(row['Pagamento']) if pd.notna(row['Pagamento']) else "-"
        pdf.cell(col_widths_detailed[5], 6, txt=payment[:12], border=1)
        pdf.ln()

    pdf.ln(10)

    # Mensagem final
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(255, 102, 0)
    pdf.cell(page_width, 10, txt="Keep shining!", ln=1, align='C')

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(page_width, 6, txt="Bright N Shine Pet Dental LLC", ln=1, align='C')
    pdf.cell(page_width, 6, txt="(407)259-7897", ln=1, align='C')

    return pdf
