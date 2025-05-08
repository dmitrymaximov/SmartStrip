'''
@app.get("/oauth/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code from Yandex"),
    state: str | None = Query(None, description="Optional state"),
):
    """
    Получаем code из запроса, обмениваем его на access_token + refresh_token,
    создаём User и сохраняем его в users_cache.
    В конце — редиректим пользователя на какую-нибудь страницу (или отдаем HTML).
    """
    # 1) Обмениваем code на токены
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": app_config.client_id,
        "client_secret": app_config.client_secret,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(YANDEX_TOKEN_URL, data=data)
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token exchange failed: {resp.text}"
        )
    token_data = resp.json()
    access_token = token_data["access_token"]
    expires_in = token_data.get("expires_in", 3600)
    refresh_token = token_data.get("refresh_token")

    # 2) Получаем информацию о пользователе
    async with httpx.AsyncClient() as client:
        userinfo_resp = await client.get(
            "https://login.yandex.ru/info?format=json",
            headers={"Authorization": f"OAuth {access_token}"}
        )
    if userinfo_resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch userinfo: {userinfo_resp.text}"
        )
    userinfo = userinfo_resp.json()

    # 3) Создаём экземпляр User и сохраняем в кэш
    user = User(
        user_id=userinfo["id"],
        display_name=userinfo.get("display_name"),
        email=userinfo.get("default_email"),
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    )
    users_cache[user.user_id] = user

    # 4) Редирект (или можно вернуть JSON/HTML)
    # Предположим, у тебя есть фронтенд на http://localhost:3000/success
    redirect_url = f"https://your.frontend.domain/success?user_id={user.user_id}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
'''


