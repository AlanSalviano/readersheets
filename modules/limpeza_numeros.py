import streamlit as st
import re

def limpeza_numeros_page():
    """
    Renderiza a página para limpar e formatar números de telefone.
    """
    st.title("Limpeza de Números de Telefone")
    st.markdown("---")
    
    st.info("Insira um ou mais números de telefone abaixo. O aplicativo removerá automaticamente os caracteres indesejados.")
    
    input_text = st.text_area(
        "Insira os números de telefone:",
        height=200,
        placeholder="Cole aqui uma lista de números. Cada número pode estar em uma nova linha.",
    )

    if st.button("Limpar e Formatar"):
        if input_text:
            # Divide o texto em linhas para processar cada número separadamente
            numbers = input_text.splitlines()
            cleaned_numbers = []
            
            for number in numbers:
                # Remove todos os caracteres que não são dígitos (0-9)
                cleaned_number = re.sub(r'[^0-9]', '', number)
                if cleaned_number:
                    cleaned_numbers.append(cleaned_number)

            if cleaned_numbers:
                st.subheader("Números Limpos:")
                st.code("\n".join(cleaned_numbers))
            else:
                st.warning("Nenhum número válido foi encontrado. Por favor, insira números que contenham dígitos.")
        else:
            st.warning("Por favor, insira um número de telefone para continuar.")
