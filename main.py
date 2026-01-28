import asyncio
import typer
import keyring  
from pesuacademy import PESUAcademy
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from typing import List,Optional
import inquirer
import os
import requests
from bs4 import BeautifulSoup
import time

app = typer.Typer()
SERVICE_ID = "pes_cli" 
console=Console()

def clear_screen():
    """Clears the terminal screen for Windows, Linux, and macOS."""
    if os.name == 'nt':
        # For Windows
        _ = os.system('cls')
    else:
        # For macOS and Linux (posix)
        _ = os.system('clear')

async def get_student():
    username = "PES1UG25CS258" #
    password = keyring.get_password(SERVICE_ID, username)
    
    if not password:
        print("❌ No credentials found. Run 'login' first.")
        return None
    
    student = await PESUAcademy.login(username, password)
    return student

@app.command()
def login(username: str, password: str):
    try:
        asyncio.run(PESUAcademy.login(username, password))
        print("Login Valid!")

        keyring.set_password(SERVICE_ID, username, password)        
    except Exception as e:
        print(f"Login failed: {e}")

@app.command()
def attendance():
    async def _logic():
        student = await get_student()
        if student:
            att=await student.get_attendance()
            table=Table(title='Attendance')
            table.add_column(header='Course Titile')
            table.add_column(header='Attendance')
            table.add_column(header='Total Classes')
            for item in att[1]:
                table.add_row(item.title,str(item.attendance.percentage),str(item.attendance.attended)+'/'+str(item.attendance.total))
            console.print(table)
            
        else:
            print('-login first')
            
    asyncio.run(_logic())
@app.command('courses')
def view_courses():
    async def _logic():
        student=await get_student()
        if student:
            courses=await student.get_courses()
            table=Table(title='Courses')
            
            table.add_column(header='Course Code')
            table.add_column(header='Course Title')

            for course in courses[1]:
                table.add_row(course.code,course.title)
            console.print(table)
            profile=await student.get_profile()
            print(profile.personal.semester)
            
            
            
    asyncio.run(_logic())

@app.command('syllabus')
def view_syllabus(course_codes: List[str] = typer.Argument(..., help="One or more Subject Codes (e.g. UE25CS151A)") ,units: Optional[List[int]] = typer.Option(
        None, "--unit", "-u", help="Filter by Unit Number (1, 2, etc.)"
    )):
    async def _logic():
        student=await get_student()
        if student:
            courses=await student.get_courses()
            id_courseId={}
            
            
            for course in courses[1]:
                id_courseId[course.code]=course.id
            
            for course_code in course_codes:
                if course_code in id_courseId:
                    root_tree=Tree("Course Syllabus:{}".format(course_code))
                    
                    all_units=await student.get_units_for_course(id_courseId[course_code])
                    if units:
                        all_units=list(filter(lambda x:(all_units.index(x)+1)in units,all_units))
                    
                    for unit in all_units:
                        unit_tree=root_tree.add(unit.title.strip())
                        topics=await student.get_topics_for_unit(unit.id)
                        for topic in topics:
                            unit_tree.add(topic.title)
                    console.print(root_tree)                
    asyncio.run(_logic())
def create_authenticated_session():
    """Create and return an authenticated session"""
    session = requests.Session()
    
    login_url = "https://www.pesuacademy.com/Academy/j_spring_security_check"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Referer": "https://www.pesuacademy.com/Academy/"
    }
    
    response = session.get("https://www.pesuacademy.com/Academy/", headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': '_csrf'})['value']
    
    login_data = {
        "j_username": "PES1UG25CS258",
        "j_password": "lohithk@123",
        "_csrf": csrf_token
    }
    
    response = session.post(login_url, data=login_data, headers=headers)
    print("Warming up session...")
    session.get("https://www.pesuacademy.com/Academy/a/dashboard")
    time.sleep(2)
    
    if response.status_code == 200 or response.status_code == 302:
        print("✓ Session authenticated!")
        return session, headers
    else:
        print(f"Login failed. Status code: {response.status_code}")
        return None, None

def download_file(link, session, headers):
    """Download a single file using existing session"""
    try:
        print(f"Downloading: {link.title}...")
        
        pdf_url = link.url
        pdf_res = session.get(pdf_url, headers=headers)
        
        if pdf_res.status_code != 200:
            print(f"❌ Failed to download {link.title} - Status: {pdf_res.status_code}")
            return
        
        content = pdf_res.content[:10]
        
        # Determine file type
        file_type = 'pdf'
        if b'%PDF' in content:
            file_type = 'pdf'
        elif b'PK' in content:
            file_type = 'pptx'
        else:
            file_type ='ppt'
        
        # Sanitize filename
        safe_filename = "".join(c for c in link.title if c.isalnum() or c in (' ', '-', '_')).strip()
        filepath = f"{safe_filename}.{file_type}"
        
        with open(filepath, "wb") as f:
            f.write(pdf_res.content)
            print(f"✓ Downloaded: {filepath} ({len(pdf_res.content)} bytes)")
        
        # Small delay between downloads
        time.sleep(1)
        
    except Exception as e:
        print(f"❌ Error downloading {link.title}: {e}")

@app.command()
def download():
    async def _logic():
        student = await get_student()
        courses = await student.get_courses()
        courses_names = [course.title for course in courses[1]]
        
        questions = [
            inquirer.List('course',
                message="Choose a course", choices=courses_names)
        ]
        course_opt = inquirer.prompt(questions)
        selected_course = course_opt['course']
        course_id = [course.id for course in courses[1] if course.title == selected_course][0]
        
        units = await student.get_units_for_course(course_id=course_id)
        unit_opt = [
            inquirer.List('units',
                message='Choose a unit', choices=[unit.title for unit in units])
        ]
        unit_prompt = inquirer.prompt(unit_opt)
        selected_unit = unit_prompt['units']
        unit_id = [unit.id for unit in units if unit.title == selected_unit][0]
        
        topics = await student.get_topics_for_unit(unit_id=unit_id)
        topics_opt = [
            inquirer.Checkbox('topics',
                message='Choose topics (use space to select, enter to confirm)',
                choices=[topic.title for topic in topics],
            )
        ]
        topic_prompt = inquirer.prompt(topics_opt)
        topic_ans = topic_prompt['topics']
        filtered_topics = list(filter(lambda x: x.title in topic_ans, topics))
        
        # Collect ALL links first
        all_links = []
        for topic in filtered_topics:
            material_links = await student.get_material_links(topic=topic, material_type_id=2)
            if material_links:
                all_links.extend(material_links)
        
        if not all_links:
            print("No materials found!")
            return
        
        print(f"Found {len(all_links)} files to download\n")
        
        # Create session once
        session, headers = create_authenticated_session()
        
        if not session:
            print("❌ Failed to authenticate")
            return
        
        try:
            # Download all files
            for idx, link in enumerate(all_links, 1):
                print(f"[{idx}/{len(all_links)}]", end=" ")
                download_file(link, session, headers)
        finally:
            session.close()
            print("\n✓ All downloads completed!")

    asyncio.run(_logic())

@app.command('timetable')
def timetable():
    async def _logic():
        pass

        
if __name__ == "__main__":
    app()