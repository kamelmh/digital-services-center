from fpdf import FPDF
import os

class EmailPDF(FPDF):
    def header(self):
        # Blue header line
        self.set_draw_color(44, 90, 160)
        self.set_line_width(0.5)
        self.line(10, 15, 200, 15)
        
        # Name
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(44, 90, 160)
        self.set_y(20)
        self.cell(0, 10, 'Kamel Mahi', ln=True)
        
        # Title
        self.set_font('Helvetica', '', 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, 'Enseignant certifie - Informatique & Gestion de stock', ln=True)
        
        # Contact
        self.set_font('Helvetica', '', 9)
        self.set_text_color(136, 136, 136)
        self.cell(0, 5, 'kamelmahi71@gmail.com | +213 676 77 38 92 | El Bayadh, Algerie', ln=True)
        
        self.ln(10)

def create_director_email():
    pdf = EmailPDF()
    pdf.add_page()
    
    # Subject box
    pdf.set_fill_color(240, 244, 248)
    pdf.set_draw_color(44, 90, 160)
    pdf.rect(10, pdf.get_y(), 190, 12, 'D')
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(5, 8, '', ln=False)
    pdf.cell(0, 8, 'Objet : Demande de collaboration - Projet de recherche sur l\'apprentissage assiste par IA en anglais', ln=True)
    pdf.ln(8)
    
    # Content
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(51, 51, 51)
    
    pdf.cell(0, 8, 'Bonjour Monsieur/Madame le Directeur,', ln=True)
    pdf.ln(5)
    
    pdf.multi_cell(0, 6, 'Je me permets de vous contacter dans le cadre d\'un projet de recherche academique que je mene sur l\'integration de l\'intelligence artificielle dans l\'enseignement de l\'anglais en Algerie.')
    pdf.ln(5)
    
    pdf.multi_cell(0, 6, 'Le projet, intitule Ta\'allim, developpe une application mobile qui genere automatiquement des exercices bilingues (arabe/francais) adaptes au programme national. L\'application propose :')
    pdf.ln(3)
    
    # Bullet points
    bullets = [
        'Des exercices de grammaire (60 structures couvrant les niveaux 1AM-4AM, CEFR A1-B1)',
        'Un vocabulaire thematique (60 mots organises par niveau)',
        'Un systeme de suivi pour les enseignants',
        'Un mode hors ligne (pas besoin d\'internet)'
    ]
    
    for bullet in bullets:
        pdf.cell(10, 6, '', ln=False)
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(5, 6, '-', ln=False)
        pdf.cell(0, 6, bullet, ln=True)
    
    pdf.ln(5)
    
    # What I'm asking
    pdf.set_fill_color(255, 253, 231)
    pdf.rect(10, pdf.get_y(), 190, 35, 'F')
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(5, 8, '', ln=False)
    pdf.cell(0, 8, 'Ce que je demande :', ln=True)
    pdf.set_font('Helvetica', '', 11)
    
    asks = [
        'L\'autorisation de mener une etude pilote de 6 semaines dans votre etablissement',
        'La participation d\'environ 60 eleves de la section moyen (1AM-4AM)',
        'La collaboration de 2 enseignants d\'anglais'
    ]
    
    for ask in asks:
        pdf.cell(10, 6, '', ln=False)
        pdf.cell(5, 6, '-', ln=False)
        pdf.cell(0, 6, ask, ln=True)
    
    pdf.ln(5)
    
    # What I'm offering
    pdf.set_fill_color(255, 253, 231)
    pdf.rect(10, pdf.get_y(), 190, 35, 'F')
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(5, 8, '', ln=False)
    pdf.cell(0, 8, 'En echange :', ln=True)
    pdf.set_font('Helvetica', '', 11)
    
    offers = [
        'Un rapport detaille sur les progres des eleves participants',
        'Un acces gratuit a l\'application pour votre etablissement',
        'Une mention dans la publication scientifique prevue'
    ]
    
    for offer in offers:
        pdf.cell(10, 6, '', ln=False)
        pdf.cell(5, 6, '-', ln=False)
        pdf.cell(0, 6, offer, ln=True)
    
    pdf.ln(8)
    
    pdf.multi_cell(0, 6, 'L\'etude est encadree academiquement et sera publiee dans une revue indexee (ASJP/Scopus).')
    pdf.ln(5)
    
    pdf.multi_cell(0, 6, 'Je me tiens a votre disposition pour une presentation detaillee du projet. Je suis disponible pour un rendez-vous a votre convenance.')
    pdf.ln(8)
    
    pdf.cell(0, 6, 'Cordialement,', ln=True)
    pdf.ln(15)
    
    # Signature
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, 'Kamel Mahi', ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'Enseignant certifie - Informatique & Gestion de stock', ln=True)
    pdf.cell(0, 5, 'El Bayadh, Algerie', ln=True)
    
    # Footer
    pdf.set_y(-30)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'kamelmahi71@gmail.com | +213 676 77 38 92', ln=True)
    
    output_path = r'C:\Users\Admin\projects\active\digital-services-center\email_director_allal.pdf'
    pdf.output(output_path)
    print(f'Director email PDF created: {output_path}')

def create_teacher_email():
    pdf = EmailPDF()
    pdf.add_page()
    
    # Subject box
    pdf.set_fill_color(240, 244, 248)
    pdf.set_draw_color(44, 90, 160)
    pdf.rect(10, pdf.get_y(), 190, 12, 'D')
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(5, 8, '', ln=False)
    pdf.cell(0, 8, 'Objet : Collaboration - Etude pilote Ta\'allim (exercices d\'anglais par IA)', ln=True)
    pdf.ln(8)
    
    # Content
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(51, 51, 51)
    
    pdf.cell(0, 8, 'Bonjour,', ln=True)
    pdf.ln(5)
    
    pdf.multi_cell(0, 6, 'Je suis Kamel Mahi, collegue enseignant a Allal. Je developpe une application mobile (Ta\'allim) qui genere automatiquement des exercices d\'anglais adaptes au programme national.')
    pdf.ln(5)
    
    pdf.multi_cell(0, 6, 'Je recherche 2 enseignants d\'anglais pour participer a une etude pilote de 6 semaines. Voici ce que ca implique :')
    pdf.ln(5)
    
    # What I'm asking
    pdf.set_fill_color(255, 253, 231)
    pdf.rect(10, pdf.get_y(), 190, 35, 'F')
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(5, 8, '', ln=False)
    pdf.cell(0, 8, 'Engagement :', ln=True)
    pdf.set_font('Helvetica', '', 11)
    
    asks = [
        'Utiliser l\'application dans vos classes (20 min, 4 fois par semaine)',
        'Faire passer un pre-test et un post-test a vos eleves',
        'Repondre a un court questionnaire et participer a un entretien (15 min)'
    ]
    
    for ask in asks:
        pdf.cell(10, 6, '', ln=False)
        pdf.cell(5, 6, '-', ln=False)
        pdf.cell(0, 6, ask, ln=True)
    
    pdf.ln(5)
    
    # What I'm offering
    pdf.set_fill_color(255, 253, 231)
    pdf.rect(10, pdf.get_y(), 190, 25, 'F')
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(5, 8, '', ln=False)
    pdf.cell(0, 8, 'En echange :', ln=True)
    pdf.set_font('Helvetica', '', 11)
    
    offers = [
        'Un acces gratuit a l\'application',
        'Un rapport sur les progres de vos eleves'
    ]
    
    for offer in offers:
        pdf.cell(10, 6, '', ln=False)
        pdf.cell(5, 6, '-', ln=False)
        pdf.cell(0, 6, offer, ln=True)
    
    pdf.ln(8)
    
    pdf.multi_cell(0, 6, 'Interesse(e) ? On peut en discuter de vive voix quand vous etes disponible.')
    pdf.ln(8)
    
    pdf.cell(0, 6, 'Cordialement,', ln=True)
    pdf.ln(15)
    
    # Signature
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, 'Kamel Mahi', ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'Enseignant certifie - Informatique & Gestion de stock', ln=True)
    
    # Footer
    pdf.set_y(-30)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'kamelmahi71@gmail.com | +213 676 77 38 92', ln=True)
    
    output_path = r'C:\Users\Admin\projects\active\digital-services-center\email_teacher_allal.pdf'
    pdf.output(output_path)
    print(f'Teacher email PDF created: {output_path}')

if __name__ == '__main__':
    create_director_email()
    create_teacher_email()
    print('Both PDFs created successfully!')
