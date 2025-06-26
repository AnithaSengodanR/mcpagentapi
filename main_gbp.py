import sqlite3
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import httpx
import os
from bs4 import BeautifulSoup # type: ignore
import json
import logging

load_dotenv()

# initialize server
mcp = FastMCP("GBP API", version="1.0.0", description="GBP API for TCS Bancs",
              base_url="https://demoapps.tcsbancs.com/Core/")

USER_AGENT = "news-app/1.0"
logger = logging.getLogger("httpx")
GBP_APIS = {
    "CashblockList": "https://demoapps.tcsbancs.com/Core/accountManagement/account/blockList/{account_no}?pageNum=1&PageSize=22",
    "AccountDetailList": "https://demoapps.tcsbancs.com/Core/accountManagement/account/balanceDetails/{account_no}?pageNum=1&PageSize=22"
}


async def fetch_GBPData(url: str):
    """It pulls and summarizes the List of cash blocks on an account."""
    async with httpx.AsyncClient() as client:
        try:
            logging.info(f"[DEBUG]Fetching data from {url}...")
           ## url ="https://demoapps.tcsbancs.com/Core/accountManagement/account/blockList/101000000101814?pageNum=1&PageSize=22"
            headers = {'userId': '1',
                       'entity': 'GPRDTTSTOU',
                       'languageCode': '1',
                       "Accept": "application/json"}
           ## print.log(f"[DEBUG]Fetching data from {url}...");
           
            response = await client.get(url,headers=headers, timeout=30.0)
           # logging.info("Response"+response.text );
            #logging.info("Response in Json"+response.json() );
         ##   soup = BeautifulSoup(response.text, "html.parser")
           ## paragraphs = soup.find_all("p")
            ##text = " ".join([p.get_text() for p in paragraphs[:5]]) 
            ##return text
            return response.json()
        except httpx.TimeoutException:
            return "Timeout error"

@mcp.tool()  
async def get_account_cashblks(account_no: str):
    """
    Fetches the List of Cashblocks created for an account.
    """
    url = GBP_APIS['CashblockList'].format(account_no=account_no)
    cashblock_list = await fetch_GBPData(url)
    return cashblock_list

@mcp.tool()
async def get_account_details(account_no: str):
    """
    Fetches the Account Balance Information of the given Account number.
    """
    url = GBP_APIS['AccountDetailList'].format(account_no=account_no)
    account_balance = await fetch_GBPData(url)
    return account_balance
@mcp.tool()
def list_accounts() -> list[dict]:
    
    """Returns account number, holder name, and balance from the local SQLite DB."""
    con = sqlite3.connect("C:/Users/AnithaS/WorkItem/mcp-server-project/mcp-server-project/example.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT account_no, holder_name, balance FROM accounts")
    rows = cur.fetchall()
    con.close()
    return [dict(row) for row in rows]
if __name__ == "__main__":
    mcp.run(transport="stdio")