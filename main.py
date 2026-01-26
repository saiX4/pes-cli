import asyncio
import typer
import keyring  
from pesuacademy import PESUAcademy
from rich.console import Console
from rich.table import Table

app = typer.Typer()
SERVICE_ID = "pes_cli"  # The name of your app in the vault
console=Console()

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
        print("✅ Login Valid!")

        keyring.set_password(SERVICE_ID, username, password)        
    except Exception as e:
        print(f"❌ Login failed: {e}")

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

if __name__ == "__main__":
    app()