from bs4 import BeautifulSoup
import json
import os

def extract_company_info(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initialize company info dictionary
    company_info = {
        'name': '',
        'address': '',
        'phone': '',
        'email': '',
        'vat_id': '',
        'court_registration': '',
        'managing_directors': []
    }
    
    
    # Find the imprint section
    imprint_section = soup.find('div', {'id': 'imprint'})
    if imprint_section:
        content = imprint_section.find_next('div', class_='pl_accordion__content')
        if content:
            paragraphs = content.find_all('p')
            # Extract company name and address from second paragraph
            if len(paragraphs) > 1:
                # Get text with line breaks preserved
                text = paragraphs[1].get_text(separator='<br>', strip=True)
                parts = text.split('<br>')
                if parts:
                    # First part is company name
                    company_info['name'] = parts[0].strip()
                    # Remaining parts form the address
                    if len(parts) > 1:
                        company_info['address'] = ' '.join(part.strip() for part in parts[1:] if part.strip())
            for p in paragraphs:
                text = p.get_text(strip=True)
                
                # Extract phone - handle both desktop and mobile versions
                if 'Telefon:' in text:
                    # Find the phone number in the paragraph
                    phone_span = p.find('span', class_='pd_hideOnMobile')
                    if phone_span:
                        company_info['phone'] = phone_span.text.strip()
                    else:
                        # Fallback to extracting from text
                        phone = text.split('Telefon:')[1].strip()
                        # Remove any HTML tags and clean up
                        phone = BeautifulSoup(phone, 'html.parser').get_text().strip()
                        company_info['phone'] = phone
                
                # Extract email
                if 'E-Mail:' in text:
                    email = text.split('E-Mail:')[1].strip()
                    company_info['email'] = email
                
                # Extract VAT ID
                if 'Umsatzsteuer-Identifikationsnr.:' in text:
                    vat_id = text.split('Umsatzsteuer-Identifikationsnr.:')[1].strip()
                    company_info['vat_id'] = vat_id
                
                # Extract court registration
                if 'Amtsgericht' in text:
                    company_info['court_registration'] = text.strip()
                
                # Extract managing directors
                if 'Vertreten durch:' in text:
                    directors = text.split('Vertreten durch:')[1].strip()
                    company_info['managing_directors'] = [d.strip() for d in directors.split(',')]
    
    return company_info

def process_html_files(directory):
    results = []
    
    # Process all HTML files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
                company_info = extract_company_info(html_content)
                results.append({
                    # 'file': filename,
                    'company_info': company_info
                })
    
    return results

def main():
    # Directory containing HTML files
    html_dir = 'otto/data'
    
    # Process all HTML files
    results = process_html_files(html_dir)
    
    # Save results to JSON file
    with open('company_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Processed {len(results)} files. Results saved to company_data.json")

if __name__ == '__main__':
    main()
