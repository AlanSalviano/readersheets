from fpdf import FPDF
from datetime import datetime
from .utils import format_currency
import math

def create_payroll_summary_with_vars_pdf(payroll_data, custom_variables, start_date, end_date):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, txt="RESUMO DO PAYROLL", ln=1, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    # Use as datas para o subtítulo
    if start_date and end_date:
        pdf.cell(190, 10, txt=f"Relatório de {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}", ln=1)
    else:
        pdf.cell(190, 10, txt="Resumo por Técnico", ln=1)
    
    pdf.ln(5)
    
    col_width = 63.3
    
    for i in range(0, len(payroll_data), 3):
        tech_group = payroll_data[i:i+3]
        
        line_height = 6
        num_lines_tech = 10  # Aumenta o número de linhas para incluir o Support Value
        block_height_tech = num_lines_tech * line_height + 2
        
        # Verifica se há espaço para o próximo grupo de técnicos
        if pdf.get_y() + block_height_tech > pdf.h - pdf.b_margin:
            pdf.add_page()
            pdf.ln(5)

        y_start = pdf.get_y()

        for j, tech_data in enumerate(tech_group):
            x_pos = 10 + j * col_width
            
            # Define a cor do bloco para os técnicos
            pdf.set_fill_color(240, 240, 240)
            pdf.set_text_color(0, 0, 0)
            
            # Desenha o retângulo de fundo e a borda
            pdf.rect(x_pos - 1, y_start - 1, col_width, block_height_tech, 'F')
            pdf.rect(x_pos - 1, y_start - 1, col_width, block_height_tech, 'D')
            
            pdf.set_xy(x_pos, y_start)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(col_width, line_height, txt=f"Técnico: {tech_data['Técnico']}", ln=1)
            pdf.set_font("Arial", size=10)
            pdf.set_x(x_pos)
            pdf.cell(col_width, line_height, txt=f"Pets: {tech_data['Total de Pets']}", ln=1)
            pdf.set_x(x_pos)
            pdf.cell(col_width, line_height, txt=f"Atendimentos: {tech_data['Total de Atendimentos']}", ln=1)
            pdf.set_x(x_pos)
            pdf.cell(col_width, line_height, txt=f"Valor Produzido: {format_currency(tech_data['Valor Produzido'])}", ln=1)
            pdf.set_x(x_pos)
            pdf.cell(col_width, line_height, txt=f"Comissão (%): {tech_data['Comissao (%)']}%", ln=1)
            pdf.set_x(x_pos)

            if tech_data['Pagamento Base'] < 900:
                pdf.set_font("Arial", 'U', 10)
                pdf.set_text_color(255, 0, 0)
            
            pdf.cell(col_width, line_height, txt=f"Pagamento Base: {format_currency(tech_data['Pagamento Base'])}", ln=1)
            pdf.set_font("Arial", '', 10)
            pdf.set_text_color(0, 0, 0)
            
            pdf.set_x(x_pos)
            pdf.cell(col_width, line_height, txt=f"Pagamento Fixo: {format_currency(tech_data['Pagamento Fixo'])}", ln=1)
            pdf.set_x(x_pos)
            
            if tech_data['Variáveis'] > 0:
                pdf.set_text_color(0, 128, 0)
            elif tech_data['Variáveis'] < 0:
                pdf.set_text_color(255, 0, 0)
            
            pdf.cell(col_width, line_height, txt=f"Variáveis: {format_currency(tech_data['Variáveis'])}", ln=1)
            pdf.set_text_color(0, 0, 0)
            
            pdf.set_x(x_pos)
            pdf.cell(col_width, line_height, txt=f"Pagamento Final: {format_currency(tech_data['Pagamento Final'])}", ln=1)
            pdf.set_x(x_pos)
            pdf.cell(col_width, line_height, txt=f"Support Value: {format_currency(tech_data['Support Value'])}", ln=1)

        pdf.set_y(y_start + block_height_tech + 5)
        pdf.set_text_color(0, 0, 0)

    if custom_variables and any(v['tech'] for v in custom_variables):
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(190, 10, txt="Variáveis Adicionais", ln=1)
        pdf.ln(5)
        
        vars_filtered = [v for v in custom_variables if v['tech']]
        
        for i in range(0, len(vars_filtered), 3):
            var_group = vars_filtered[i:i+3]
            
            line_height = 6
            num_lines_vars = 7
            block_height_vars = num_lines_vars * line_height + 2

            if pdf.get_y() + block_height_vars > pdf.h - pdf.b_margin:
                pdf.add_page()
                pdf.ln(5)
            
            y_start = pdf.get_y()
            
            for j, var_data in enumerate(var_group):
                x_pos = 10 + j * col_width
                
                total_debt = var_data['valor_da_parcela'] * var_data['total_de_parcelas']
                paid_debt = var_data['valor_da_parcela'] * var_data['parcela_atual']
                total_value = var_data['valor_da_parcela']
                
                if total_value > 0:
                    pdf.set_fill_color(220, 255, 220)
                    pdf.set_text_color(0, 100, 0)
                elif total_value < 0:
                    pdf.set_fill_color(255, 220, 220)
                    pdf.set_text_color(128, 0, 0)
                else:
                    pdf.set_fill_color(240, 240, 240)
                    pdf.set_text_color(0, 0, 0)
                
                pdf.rect(x_pos - 1, y_start - 1, col_width, block_height_vars, 'F')
                pdf.rect(x_pos - 1, y_start - 1, col_width, block_height_vars, 'D')

                pdf.set_xy(x_pos, y_start)
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(col_width, line_height, txt=f"Técnico: {var_data['tech']}", ln=1)
                pdf.set_font("Arial", size=10)
                pdf.set_x(x_pos)
                pdf.cell(col_width, line_height, txt=f"Descrição: {var_data['description']}", ln=1)
                pdf.set_x(x_pos)
                pdf.cell(col_width, line_height, txt=f"Valor da Parcela: {format_currency(var_data['valor_da_parcela'])}", ln=1)
                pdf.set_x(x_pos)
                pdf.cell(col_width, line_height, txt=f"Total de Parcelas: {var_data['total_de_parcelas']}", ln=1)
                pdf.set_x(x_pos)
                pdf.cell(col_width, line_height, txt=f"Parcela Atual: {var_data['parcela_atual']}", ln=1)
                pdf.set_x(x_pos)
                pdf.cell(col_width, line_height, txt=f"Dívida Total: {format_currency(total_debt)}", ln=1)
                pdf.set_x(x_pos)
                pdf.cell(col_width, line_height, txt=f"Dívida Paga: {format_currency(paid_debt)}", ln=1)
                
            pdf.set_y(y_start + block_height_vars + 5)
            pdf.set_text_color(0, 0, 0)

    pdf.ln(10)
    pdf.set_font("Arial", size=8)
    pdf.cell(190, 5, txt="BRIGHT N SHINE PET DENTAL LLC", ln=1, align='C')
    pdf.cell(190, 5, txt="(407)259-7897", ln=1, align='C')

    return pdf
