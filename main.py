from contextlib import asynccontextmanager
import flet as ft
import flet.fastapi as flet_fastapi
from fastapi import FastAPI
from pydantic import BaseModel
import httpx

@asynccontextmanager
async def lifespan(app: FastAPI):
    await flet_fastapi.app_manager.start()
    yield
    await flet_fastapi.app_manager.shutdown()

app = FastAPI(lifespan=lifespan)

class LoginRequest(BaseModel):
    id: str
    password: str

@app.post("/api/login")
async def login(request: LoginRequest):
    id = request.id
    password = request.password
    return {
        "message": "Login successful",
        "id": id,
        "password": password
    }

@app.get("/api/gettest")
async def test():
    return {"message": "gettest successful"}

async def fletapp(page: ft.Page):
    id_input = ft.TextField(label="ID")
    password_input = ft.TextField(label="PASSWORD")
    result_text = ft.Text("Login verification")

    async def login(e):
        login_data = {
            "id": id_input.value,
            "password": password_input.value
        }
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/api/login",
                                         json=login_data)
            if response.status_code == 200:
                result = response.json()
                result_text.value = result.get("message") + " " + result.get(
                    "id") + " " + result.get("password")
            else:
                result_text.value = "Login failed"
        await page.update_async()

    async def gettest(e):
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/gettest")
            if response.status_code == 200:
                result = response.json()
                result_text.value = result.get("message")
            else:
                result_text.value = "gettest failed"
        await page.update_async()

    async def go_init(e):
        await page.go_async("/")

    async def go_fletapptask(e):
        await page.go_async("/fletapptask")

    async def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    id_input,
                    password_input,
                    ft.ElevatedButton(
                        text="Login",
                        on_click=login),
                    ft.ElevatedButton(
                        text="gettest",
                        on_click=gettest),
                    ft.ElevatedButton(
                        text="Go to Task Screen", on_click=go_fletapptask
                    ),
                    result_text,
                ],
            ))
        if page.route == "/fletapptask":
            page.views.append(
                ft.View(
                    "/fletapptask",
                    [
                        ft.AppBar(title=ft.Text("Task Screen"),
                                  bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ElevatedButton(
                            "Go Home", on_click=go_init
                        ),
                    ],
                ))
        await page.update_async()

    async def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        await page.go_async(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    await page.go_async(page.route)

flet_app = flet_fastapi.app(fletapp)
app.mount("/", flet_app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1")

