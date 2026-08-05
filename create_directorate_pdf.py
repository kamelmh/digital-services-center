from fpdf import FPDF

class EmailPDF(FPDF):
    def header(self):
        self.set_draw_color(44, 90, 160)
        self.set_line_width(0.5)
        self.line(10, 15, 200, 15)
        
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(44, 90, 160)
        self.set_y(20)
        self.cell(0, 10, 'Kamel Mahi', new_x="LMARGIN", new_y="NEXT")
        
        self.set_font('Helvetica', '', 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, 'Enseignant certifie - Informatique & Gestion de stock', new_x="LMARGIN", new_y="NEXT")
        
        self.set_font('Helvetica', '', 9)
        self.set_text_color(136, 136, 136)
        self.cell(0, 5, 'kamelmahi71@gmail.com | +213 676 77 38 92 | El Bayadh, Algerie', new_x="LMARGIN", new_y="NEXT")
        
        self.ln(10)

def create_directorate_email():
    pdf = EmailPDF()
    pdf.add_page()
    
    # Subject box
    pdf.set_fill_color(240, 244, 248)
    pdf.set_draw_color(44, 90, 160)
    pdf.rect(10, pdf.get_y(), 190, 12, 'D')
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(5, 8, '', new_x="RIGHT", new_y="TOP")
    pdf.cell(0, 8, 'Objet : Demande de partenariat - Application mobile pour l\'enseignement de l\'anglais', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    
    # Content
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(51, 51, 51)
    
    pdf.cell(0, 8, 'Monsieur le Directeur de l\'education de la wilaya d\'El Bayadh,', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.multi_cell(0, 6, 'J\'ai l\'honneur de solliciter votre bienveillance dans le cadre d\'un projet de recherche academique visant a ameliorer l\'enseignement de l\'anglais dans les etablissements scolaires de la wilaya d\'El Bayadh.')
    pdf.ln(5)
    
    pdf.multi_cell(0, 6, 'Dans le cadre de mon travail de recherche en didactique des langues, j\'ai developpe une application mobile baptisee Ta\'allim, qui genere automatiquement des exercices d\'anglais bilingues (arabe/francais) conformes au programme national. Cette application offre :')
    pdf.ln(3)
    
    bullets = [
        '60 exercices de grammaire couvrant les niveaux 1AM-4AM (CEFR A1-B1)',
        '60 mots de vocabulaire thematiques organises par niveau',
        'Un systeme de suivi individualise des progres des eleves',
        'Un fonctionnement hors ligne (sans connexion internet)'
    ]
    
    for bullet in bullets:
        pdf.cell(10, 6, '', new_x="RIGHT", new_y="TOP")
        pdf.cell(5, 6, '-', new_x="RIGHT", new_y="TOP")
        pdf.cell(0, 6, bullet, new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(5)
    
    # What I'm asking
    pdf.set_fill_color(255, 253, 231)
    pdf.rect(10, pdf.get_y(), 190, 35, 'F')
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(5, 8, '', new_x="RIGHT", new_y="TOP")
    pdf.cell(0, 8, 'Objectif de la demarche :', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 11)
    
    pdf.cell(10, 6, '', new_x="RIGHT", new_y="TOP")
    pdf.cell(5, 6, '-', new_x="RIGHT", new_y="TOP")
    pdf.cell(0, 6, 'Mener une etude pilote de 6 semaines dans 2-3 etablissements de la wilaya', new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(10, 6, '', new_x="RIGHT", new_y="TOP")
    pdf.cell(5, 6, '-', new_x="RIGHT", new_y="TOP")
    pdf.cell(0, 6, 'Impliquer environ 60 eleves et 2-4 enseignants d\'anglais', new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(10, 6, '', new_x="RIGHT", new_y="TOP")
    pdf.cell(5, 6, '-', new_x="RIGHT", new_y="TOP")
    pdf.cell(0, 6, 'Evaluer l\'impact sur l\'apprentissage via une methode scientifique', new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(5)
    
    # What I'm offering
    pdf.set_fill_color(255, 253, 231)
    pdf.rect(10, pdf.get_y(), 190, 35, 'F')
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(5, 8, '', new_x="RIGHT", new_y="TOP")
    pdf.cell(0, 8, 'En echange :', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 11)
    
    offers = [
        'Un rapport detaille sur les resultats de l\'etude',
        'Un accès gratuit a l\'application pour les etablissements participants',
        'Une mention dans la publication scientifique prevue (ASJP/Scopus)',
        'Une presentation des resultats a la direction de l\'education'
    ]
    
    for offer in offers:
        pdf.cell(10, 6, '', new_x="RIGHT", new_y="TOP")
        pdf.cell(5, 6, '-', new_x="RIGHT", new_y="TOP")
        pdf.cell(0, 6, offer, new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(8)
    
    pdf.multi_cell(0, 6, 'Cette initiative s\'inscrit dans la dynamique de modernisation de l\'enseignement et de l\'utilisation des technologies dans l\'education. Elle beneficie d\'un encadrement academique rigoureux et sera publiee dans une revue scientifique indexee.')
    pdf.ln(5)
    
    pdf.multi_cell(0, 6, 'Je me tiens a votre entiere disposition pour vous presenter ce projet en detail et discuter des modalites de collaboration. Je suis disponible a votre convenance.')
    pdf.ln(8)
    
    pdf.cell(0, 6, 'Je vous prie d\'agreer, Monsieur le Directeur, l\'expression de ma haute consideration.', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    
    # Signature
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, 'Kamel Mahi', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'Enseignant certifie - Informatique & Gestion de stock', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, 'El Bayadh, Algerie', new_x="LMARGIN", new_y="NEXT")
    
    # Footer
    pdf.set_y(-30)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'kamelmahi71@gmail.com | +213 676 77 38 92', new_x="LMARGIN", new_y="NEXT")
    
    output_path = r'C:\Users\Admin\projects\active\digital-services-center\email_directorate_education.pdf'
    pdf.output(output_path)
    print(f'Directorate email PDF created: {output_path}')

def create_directorate_whatsapp():
    pdf = EmailPDF()
    pdf.add_page()
    
    # Header
    pdf.set_fill_color(37, 211, 102)
    pdf.rect(10, pdf.get_y(), 190, 12, 'F')
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(5, 8, '', new_x="RIGHT", new_y="TOP")
    pdf.cell(0, 8, 'Message WhatsApp - Direction de l\'education', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    
    # Content
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(51, 51, 51)
    
    pdf.multi_cell(0, 6, 'Bonjour Monsieur le Directeur,')
    pdf.ln(3)
    
    pdf.multi_cell(0, 6, 'Je suis Kamel Mahi, enseignant certifie a l\'ecole Allal. Je mene un projet de recherche sur l\'utilisation de l\'IA dans l\'enseignement de l\'anglais (application mobile generant des exercices automatiques).')
    pdf.ln(3)
    
    pdf.multi_cell(0, 6, 'Je souhaite mener une etude pilote de 6 semaines dans 2-3 etablissements de la wilaya (environ 60 eleves + 2-4 enseignants d\'anglais). Methodologie rigoureuse, consentement eclaire, publication prevue.')
    pdf.ln(3)
    
    pdf.multi_cell(0, 6, 'Pourrions-nous nous rencontrer brievement pour en discuter ?')
    pdf.ln(3)
    
    pdf.multi_cell(0, 6, 'Merci de votre attention,')
    pdf.ln(3)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, 'Kamel Mahi', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'kamelmahi71@gmail.com | +213 676 77 38 92', new_x="LMARGIN", new_y="NEXT")
    
    output_path = r'C:\Users\Admin\projects\active\digital-services-center\whatsapp_directorate_education.pdf'
    pdf.output(output_path)
    print(f'Directorate WhatsApp PDF created: {output_path}')

if __name__ == '__main__':
    create_directorate_email()
    create_directorate_whatsapp()
    print('Both Directorate PDFs created successfully!')
