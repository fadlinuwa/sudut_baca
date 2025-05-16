from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx, requests as r
from fastapi.responses import RedirectResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

GUTENDEX_API = "https://gutendex.com/books/"

# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request, search: str = None):
#     params = {"search": search} if search else {}
#     async with httpx.AsyncClient() as client:
#         response = await client.get(GUTENDEX_API, params=params)
#         data = response.json()
        
#         books = data.get("results", [])
#         next = data.get("next", [])
#         return templates.TemplateResponse("index.html", {
#             "request": request,
#             "books": books,
#             "search": search
#         })
    
    # response = r.get(GUTENDEX_API, params=params)
    # data = response.json()
    
    # books = data.get("results", [])
    # return templates.TemplateResponse("index.html", {
    #     "request": request,
    #     "books": books,
    #     "search": search
    # })

@app.get("/404", response_class=HTMLResponse)
async def not_found_page(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})

@app.get("/500")
async def internal_error_page(request: Request):
    return templates.TemplateResponse("500.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, page: int = 1, search: str = None):
    params = {"page": page}
    if search:
        params["search"] = search

    async with httpx.AsyncClient() as client:
        response = await client.get(GUTENDEX_API, params=params)
        data = response.json()

    books = data.get("results", [])
    count = data.get("count", 0)

    total_pages = (count // 32) + (1 if count % 32 > 0 else 0)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "books": books,
        "search": search,
        "page": page,
        "total_pages": total_pages,
    })

@app.get("/baca/{book_id}")
async def baca_buku(request: Request, book_id: int):
    async with httpx.AsyncClient() as client:
        url = f"https://gutendex.com/books/{book_id}/"
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            html_url = data["formats"].get("text/html") or \
                        data["formats"].get("text/html; charset=utf-8")
            if html_url:
                return templates.TemplateResponse("baca.html", {
                    "request": request,
                    "judul": data["title"],
                    "link_baca": html_url
                })
    
    # url = f"https://gutendex.com/books/{book_id}/"
    # response = r.get(url)
    # if response.status_code == 200:
    #     data = response.json()
    #     html_url = data["formats"].get("text/html") or \
    #                 data["formats"].get("text/html; charset=utf-8")
    #     if html_url:
    #         return templates.TemplateResponse("baca.html", {
    #             "request": request,
    #             "judul": data["title"],
    #             "link_baca": html_url
    #         })
    return RedirectResponse("/404")

@app.get("/detail/{book_id}")
async def baca_buku(request: Request, book_id: int, search: str = None):
    async with httpx.AsyncClient() as client:
        url = f"https://gutendex.com/books/{book_id}/"
        response = await client.get(url)
        if response.status_code == 200:
            books = response.json()

            return templates.TemplateResponse("detail.html", {
                "request": request,
                "books": books,
                "search": search
            })
    return RedirectResponse("/404")

