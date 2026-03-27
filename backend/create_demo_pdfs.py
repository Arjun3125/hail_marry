#!/usr/bin/env python3
"""
Create demo PDF documents with educational content for VidyaOS.
Generates real PDFs that can be ingested through the RAG pipeline.
"""
import os
from pathlib import Path
from fpdf import FPDF


class DemoPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, 'VidyaOS Demo School - Educational Content', ln=True, align='C')
        self.ln(5)
        self.set_draw_color(0, 51, 102)
        self.line(10, 25, 200, 25)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def section_title(self, title):
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(51, 51, 51)
        self.cell(0, 8, title, ln=True)
        self.ln(1)

    def body_text(self, text):
        self.set_font('helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, text)
        self.ln(2)


def create_mathematics_pdf(output_path):
    """Create Mathematics NCERT-style content about Quadratic Equations."""
    pdf = DemoPDF()
    pdf.add_page()
    pdf.chapter_title('Mathematics - Chapter 4: Quadratic Equations')

    pdf.section_title('Chapter Overview')
    pdf.body_text(
        "A quadratic equation in the variable x is an equation of the form ax^2 + bx + c = 0, "
        "where a, b, c are real numbers, a is not equal to 0. This is called the standard form of a "
        "quadratic equation. Quadratic equations arise in many real-life situations such as calculating areas, "
        "projectile motion, and optimization problems."
    )

    pdf.section_title('4.1 Introduction to Quadratic Equations')
    pdf.body_text(
        "A quadratic polynomial when equated to zero becomes a quadratic equation. "
        "The standard form is: ax^2 + bx + c = 0, where a is not equal to 0. "
        "Examples include: x^2 - 5x + 6 = 0, 2x^2 + 3x - 2 = 0, and x^2 - 4 = 0."
    )

    pdf.section_title('4.2 Solution by Factorization')
    pdf.body_text(
        "If we can factorize ax^2 + bx + c into a product of two linear factors, then "
        "the roots can be found by equating each factor to zero. For example, to solve "
        "2x^2 - 5x + 3 = 0 by factorization, we write: 2x^2 - 2x - 3x + 3 = 0, "
        "which gives 2x(x - 1) - 3(x - 1) = 0, so (x - 1)(2x - 3) = 0. "
        "Therefore, x = 1 or x = 3/2."
    )

    pdf.section_title('4.3 Solution by Completing the Square')
    pdf.body_text(
        "This method works for all quadratic equations. For x^2 + 6x - 7 = 0, "
        "we first write x^2 + 6x = 7. Then add (6/2)^2 = 9 to both sides: "
        "x^2 + 6x + 9 = 7 + 9, which gives (x + 3)^2 = 16. "
        "Taking square roots: x + 3 = plus or minus 4, so x = 1 or x = -7."
    )

    pdf.section_title('4.4 Quadratic Formula')
    pdf.body_text(
        "The quadratic formula solves any equation of the form ax^2 + bx + c = 0: "
        "x = (-b plus or minus square root of (b^2 - 4ac)) / 2a. "
        "The discriminant D = b^2 - 4ac determines the nature of roots: "
        "If D greater than 0: Two distinct real roots. "
        "If D = 0: Two equal real roots. "
        "If D less than 0: No real roots (roots are complex)."
    )

    pdf.section_title('Exercise 4.1')
    pdf.body_text(
        "1. Check whether these are quadratic equations: (x + 1)^2 = 2(x - 3)\n"
        "2. Represent this situation as quadratic equation: The area of a rectangular plot is 528 sq m. "
        "The length is one more than twice its breadth.\n"
        "3. Find the roots of x^2 - 5x + 6 = 0 by factorization.\n"
        "4. Solve 2x^2 - 7x + 3 = 0 using the quadratic formula."
    )

    pdf.output(output_path)
    print(f"Created: {output_path}")
    return output_path


def create_science_pdf(output_path):
    """Create Science NCERT-style content about Photosynthesis."""
    pdf = DemoPDF()
    pdf.add_page()
    pdf.chapter_title('Biology - Chapter 6: Photosynthesis')

    pdf.section_title('Chapter Overview')
    pdf.body_text(
        "Photosynthesis is the process by which green plants synthesize food using "
        "carbon dioxide and water in the presence of sunlight and chlorophyll. "
        "Oxygen is released as a by-product. The overall equation is: "
        "6CO2 + 6H2O -> C6H12O6 + 6O2 (Carbon dioxide + Water -> Glucose + Oxygen)."
    )

    pdf.section_title('6.1 What is Photosynthesis?')
    pdf.body_text(
        "Photosynthesis is the most important biological process on Earth. It provides "
        "food for all living organisms, oxygen for respiration, and helps regulate "
        "atmospheric CO2 levels. The word comes from Greek: photo means light, "
        "and synthesis means putting together."
    )

    pdf.section_title('6.2 Site of Photosynthesis')
    pdf.body_text(
        "Photosynthesis takes place in chloroplasts, found mainly in the mesophyll "
        "cells of leaves. Chloroplasts contain chlorophyll, the green pigment that "
        "captures light energy. Chloroplast structure includes: outer membrane, "
        "inner membrane, thylakoids (disc-like structures containing chlorophyll), "
        "and stroma (fluid-filled space)."
    )

    pdf.section_title('6.3 The Process of Photosynthesis')
    pdf.body_text(
        "Stage 1 - Light Reaction (Photochemical Phase): Occurs in thylakoid membranes. "
        "Requires light energy. Splits water molecules (photolysis). Produces ATP and NADPH. "
        "Releases oxygen as by-product.\n\n"
        "Stage 2 - Dark Reaction (Biosynthetic Phase): Occurs in stroma. "
        "Does not require direct light. Uses ATP and NADPH from light reaction. "
        "Fixes CO2 into glucose through the Calvin Cycle."
    )

    pdf.section_title('6.4 Factors Affecting Photosynthesis')
    pdf.body_text(
        "1. Light Intensity: Higher intensity increases rate up to saturation point.\n"
        "2. Carbon Dioxide Concentration: More CO2 increases photosynthesis rate.\n"
        "3. Temperature: Optimal range is 25-35 degrees Celsius.\n"
        "4. Water Availability: Essential for photolysis step.\n"
        "5. Chlorophyll Concentration: More chlorophyll means more photosynthesis."
    )

    pdf.section_title('Exercise 6.1')
    pdf.body_text(
        "1. What is the equation for photosynthesis?\n"
        "2. Where does photosynthesis occur in the cell?\n"
        "3. What are the products of light reaction?\n"
        "4. Why is photosynthesis important for life on Earth?\n"
        "5. Explain the experiment to show that light is necessary for photosynthesis."
    )

    pdf.output(output_path)
    print(f"Created: {output_path}")
    return output_path


def create_english_pdf(output_path):
    """Create English content about Merchant of Venice."""
    pdf = DemoPDF()
    pdf.add_page()
    pdf.chapter_title('English Literature - The Merchant of Venice')

    pdf.section_title('Introduction')
    pdf.body_text(
        "The Merchant of Venice is one of William Shakespeare's most famous plays, "
        "written between 1596 and 1599. It is classified as a comedy but contains "
        "serious dramatic elements dealing with themes of justice, mercy, and prejudice."
    )

    pdf.section_title('Main Characters')
    pdf.body_text(
        "Antonio - A wealthy merchant of Venice who lends money to friends without interest.\n"
        "Bassanio - Antonio's friend who wants to court Portia and needs money.\n"
        "Shylock - A Jewish moneylender who demands a pound of flesh as collateral.\n"
        "Portia - A wealthy heiress of Belmont, famous for her speech on mercy.\n"
        "Jessica - Shylock's daughter who elopes with Lorenzo.\n"
        "Lorenzo - A friend of Bassanio, in love with Jessica."
    )

    pdf.section_title('Act 1 Summary')
    pdf.body_text(
        "Scene 1: Antonio is sad but does not know why. His friends suggest he might be "
        "worried about his ships at sea. Bassanio tells Antonio about his plan to court "
        "Portia, a wealthy heiress. He needs money to present himself properly. "
        "Antonio agrees to help but has no ready cash. He suggests Bassanio borrow money "
        "in Antonio's name."
    )

    pdf.body_text(
        "Scene 3: Bassanio and Antonio approach Shylock for a loan of 3000 ducats. "
        "Shylock, who hates Antonio for insulting him and his religion, initially refuses. "
        "When Antonio insists, Shylock proposes a bond: if the loan is not repaid on time, "
        "Antonio must forfeit a pound of his flesh. Antonio agrees, confident his ships "
        "will return in time."
    )

    pdf.section_title('Famous Quote')
    pdf.body_text(
        "The quality of mercy is not strained; It droppeth as the gentle rain from heaven "
        "Upon the place beneath. It is twice blest; It blesseth him that gives and him that takes. "
        "- Portia (Act 4, Scene 1). This speech emphasizes that mercy is a divine quality."
    )

    pdf.section_title('Major Themes')
    pdf.body_text(
        "1. Justice vs. Mercy: The play explores whether justice should be strict or tempered with mercy.\n"
        "2. Prejudice and Discrimination: Shylock faces religious and racial prejudice.\n"
        "3. Appearance vs. Reality: The casket test shows that outward appearance may hide inner worth.\n"
        "4. Friendship and Love: The bonds between characters show different forms of human connection."
    )

    pdf.section_title('Study Questions')
    pdf.body_text(
        "1. Why does Antonio agree to the pound of flesh bond?\n"
        "2. What does the casket test reveal about Portia's father?\n"
        "3. How does Shakespeare present Shylock?\n"
        "4. What is the significance of the pound of flesh?\n"
        "5. Explain the theme of justice versus mercy in the play."
    )

    pdf.output(output_path)
    print(f"Created: {output_path}")
    return output_path


def create_history_pdf(output_path):
    """Create History content about Indian Independence Movement."""
    pdf = DemoPDF()
    pdf.add_page()
    pdf.chapter_title('History - The Indian Independence Movement')

    pdf.section_title('Introduction')
    pdf.body_text(
        "The Indian Independence Movement was a series of activities with the ultimate "
        "goal of ending British rule in India. It lasted nearly 90 years, from the "
        "Revolt of 1857 to Independence in 1947."
    )

    pdf.section_title('1. The Revolt of 1857')
    pdf.body_text(
        "Causes: Political annexation policies (Doctrine of Lapse), economic exploitation, "
        "interference in religious practices, and the Enfield rifle cartridge issue. "
        "Leaders included Bahadur Shah Zafar in Delhi, Rani Laxmi Bai in Jhansi, "
        "and Tantia Tope in Gwalior. Results included end of East India Company rule "
        "and transfer of power to the British Crown."
    )

    pdf.section_title('2. Early Nationalist Movement (1885-1905)')
    pdf.body_text(
        "The Indian National Congress was founded in 1885 by A.O. Hume with Indian leaders. "
        "The first session was in Bombay with W.C. Bonnerjee as President. Moderate leaders "
        "included Dadabhai Naoroji (Grand Old Man of India), Surendranath Banerjee, "
        "and Gopal Krishna Gokhale. Their methods included petitions, prayers, and protests."
    )

    pdf.section_title('3. The Extremist Phase (1905-1919)')
    pdf.body_text(
        "Bal Gangadhar Tilak: Swaraj is my birthright and I shall have it. "
        "Lala Lajpat Rai: Lion of Punjab, founded Punjab National Bank. "
        "Bipin Chandra Pal: Father of Revolutionary Ideas. "
        "Partition of Bengal (1905) was annulled in 1911 after protests."
    )

    pdf.section_title('4. The Gandhian Era (1917-1947)')
    pdf.body_text(
        "Gandhi's Major Movements: Non-Cooperation Movement (1920-22) launched after "
        "Khilafat and Jallianwala Bagh. Civil Disobedience Movement (1930-34) featured "
        "the famous Dandi March for breaking salt laws. Quit India Movement (1942) "
        "used the slogan Do or Die and Britishers, Quit India!"
    )

    pdf.section_title('5. Revolutionary Movements')
    pdf.body_text(
        "Famous Revolutionaries: Bhagat Singh (martyred 1931), Chandrashekhar Azad, "
        "Subhas Chandra Bose (INA and Dilli Chalo campaign). The Jallianwala Bagh "
        "Massacre occurred on April 13, 1919, when General Dyer fired on an unarmed crowd."
    )

    pdf.section_title('6. Independence (1947)')
    pdf.body_text(
        "Mountbatten Plan (June 3, 1947) proposed partition of Bengal and Punjab. "
        "India gained independence on August 15, 1947. Key leaders included "
        "Jawaharlal Nehru (first Prime Minister), Sardar Patel (Iron Man), "
        "and Dr. B.R. Ambedkar (Father of Indian Constitution)."
    )

    pdf.section_title('Important Dates')
    pdf.body_text(
        "1857: Revolt of 1857\n"
        "1885: Indian National Congress founded\n"
        "1905: Partition of Bengal\n"
        "1919: Jallianwala Bagh Massacre\n"
        "1930: Dandi March\n"
        "1942: Quit India Movement\n"
        "1947: Independence (August 15)\n"
        "1950: Republic Day (January 26)"
    )

    pdf.output(output_path)
    print(f"Created: {output_path}")
    return output_path


def main():
    """Create all demo PDF documents."""
    output_dir = Path(__file__).parent / "demo_pdfs"
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("Creating Demo Educational PDFs for VidyaOS")
    print("=" * 60)

    pdfs_created = []

    pdfs_created.append(create_mathematics_pdf(output_dir / "NCERT_Mathematics_Ch4_Quadratics.pdf"))
    pdfs_created.append(create_science_pdf(output_dir / "NCERT_Science_Ch6_Photosynthesis.pdf"))
    pdfs_created.append(create_english_pdf(output_dir / "English_Merchant_of_Venice.pdf"))
    pdfs_created.append(create_history_pdf(output_dir / "History_Indian_Independence.pdf"))

    print("=" * 60)
    print(f"Created {len(pdfs_created)} demo PDF documents")
    print(f"Location: {output_dir}")
    print("=" * 60)
    print("\nFiles created:")
    for pdf in pdfs_created:
        size = os.path.getsize(pdf)
        print(f"  - {pdf.name} ({size:,} bytes)")

    return pdfs_created


if __name__ == "__main__":
    main()
