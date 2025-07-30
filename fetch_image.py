from pexels_api import API



with open("pexels.txt") as f:
    key = f.read()

api = API(key)

def fetch_image(query: str) -> str:

    api.search(query, page=1, results_per_page=1)

    photo = api.get_entries()

    try:
        return photo[0].original
    except:
        return "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%2Fid%2FOIP.m1hyrlLcc8OZcXReRK9O5wHaH_%3Fpid%3DApi&f=1&ipt=f147677c57fc133c88a368280fbcefc11695e1190c7d899f6e967017cff70767&ipo=images"


