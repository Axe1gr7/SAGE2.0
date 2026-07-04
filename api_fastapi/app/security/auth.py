from fastapi import status, HTTPException,Depends
from fastapi.security import HTTPBasic,HTTPBasicCredentials
import secrets

security= HTTPBasic()
def verificar_Petcion(credentials: HTTPBasicCredentials=Depends(security)):
    usuarioAuth= secrets.compare_digest(credentials.username,"a")
    contraAuth= secrets.compare_digest(credentials.password,"1310")
    
    if not(usuarioAuth and contraAuth):
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="credenciales no validas",
        )
        
    return credentials.username
