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
@app.command()
def download():
    async def _logic():
        view='home'
        student=await get_student()
        courses=await student.get_courses()
        courses_names=[course.title for course in courses[1]]
        questions=[
            inquirer.List('course',
            message="Choose a course",choices=courses_names)
        ]
        course_opt=inquirer.prompt(questions)
        selected_course=course_opt['course']
        course_id=[course.id for course in courses[1] if course.title==selected_course][0]
        units=await student.get_units_for_course(course_id=course_id)
        unit_opt=[
            inquirer.List('units',
            message='Choose a unit',choices=[unit.title for unit in units])
        ]
        unit_prompt=inquirer.prompt(unit_opt)
        selected_unit=unit_prompt['units']
        unit_id=[unit.id for unit in units if unit.title==selected_unit][0]
        topics=await student.get_topics_for_unit(unit_id=unit_id)
        topics_opt=[
            inquirer.Checkbox('topics',
                message='Choose a topic',
                choices=[topic.title for topic in topics],
                
            )
        ]
        topic_prompt=inquirer.prompt(topics_opt)
        topic_ans=topic_prompt['topics']
        print(topic_ans)


    asyncio.run(_logic())


        
if __name__ == "__main__":
    app()