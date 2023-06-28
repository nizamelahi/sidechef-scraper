import requests
from bs4 import BeautifulSoup
import json

def get_recipe_ids(mealtype):
    ids=[]
    pagenum=1
    URL = f"https://www.sidechef.com/recipes/{mealtype}/?page="
    data = requests.get(URL+str(pagenum)).json()
    while data['results'] :                                          
        for result in data['results']:
            ids.append(result['id'])
        pagenum=pagenum+1
        print(f"{mealtype}, page {pagenum}")
        data = requests.get(URL+str(pagenum)).json()
    return ids

mealtypes=["breakfast","brunch","lunch","dinner","dessert","snack"]
recipeids={}
for mealtype in mealtypes:
    print("getting ids")
    recipeids[mealtype]=get_recipe_ids(mealtype)

baseurl = "https://www.sidechef.com/recipes/"
for mealtype in mealtypes:
    recipes=[]
    for recipeid in recipeids[mealtype]:
        print(f"scraping {mealtype} ,recipe id: {recipeid}")
        page=requests.get(baseurl+str(recipeid))
        soup = BeautifulSoup(page.content,"html.parser")
        recipe={}
        if soup.find(class_="step-sequence step-placeholder body-1 rel"):           #skip incomplete recipes that redirect to other sites
            continue
        recipe['title']=soup.find(class_="h1 text-center recipe-title").text.strip()
        recipe['url']=baseurl+str(recipeid)
        imgdiv=soup.find(class_="flex flex-column align-center hero-container box-container")
        if imgdiv:
            recipe['image']=imgdiv.find("img").get('src')
        ratingdiv=soup.find(class_="ratings flex align-center")
        if ratingdiv:
            recipe['rating']=ratingdiv.find(class_="h3 rating-number").text.strip()
        recipe['totalTime']=soup.find(class_="tag-grid flex-1").find(class_="h3").text.strip()
        recipe['servings']=soup.find(class_="body-4 servings-text").text.strip()
        recipe['numIngredients']=soup.find(class_="recipe-tags caption-tag").text.strip().split(' ')[0]
        recipe['description']=soup.find(class_="recipe-description box-container text-center body-2").text.strip()

        results=soup.find(class_="ingredients wrapper")
        ingredientgroups=results.find_all(class_="ingredient-group")
        recipe['ing_group']={}
        if ingredientgroups:
            for ingredientgroup in ingredientgroups:
                gname=ingredientgroup.find(class_="group-title body-1")
                groupname=gname.text.strip() if gname else "all"
                recipe['ing_group'][groupname]=[]
                ingredientlist=ingredientgroup.find_all(class_="ingredient flex align-center")
                for ing in ingredientlist:
                    qty=ing.find(class_="deal-unit text-center body-5").text.strip()
                    ing_name=ing.find(class_="ingredient-info flex-1").text.strip()
                    recipe['ing_group'][groupname].append({"name":ing_name,"quantity":qty})
        else:
            recipe['ing_group']['all']=[]
            ingredientlist=results.find_all(class_="ingredient flex align-center")
            for ing in ingredientlist:
                qty=ing.find(class_="deal-unit text-center body-5").text.strip()
                ing_name=ing.find(class_="ingredient-info flex-1").text.strip()
                recipe['ing_group']['all'].append({"name":ing_name,"quantity":qty})

        nutritionlist=soup.find_all(class_="flex flex-column align-center nutrition-item")
        recipe['nutrition']=[]
        for item in nutritionlist:
            itemname=item.find(class_="secondary-color body-5").text.strip()
            itemvalue=item.find(class_="catrgory-value body-1").text.strip()
            recipe['nutrition'].append({itemname:itemvalue})
        
        steplist=soup.find(class_="steps wrapper bg-secondary-color").find_all(class_="step")
        recipe['tasks']=[]
        for item in steplist:
            title=item.find(class_="step-sequence body-1").text.strip()
            instruction=item.find(class_="step-description-segment")
            if instruction:
                instruction=instruction.text.strip()
                instruction=' '.join(instruction.split())
            else:
                instruction=item.find(class_="step-description body-2 content-detail-wrap").text.strip()
            visuals=item.find("amp-video")
            if visuals:
                image=visuals.get('poster')
                video=visuals.get('src')
            else:
                visuals=item.find("amp-img")
                if visuals:
                    image=visuals.get('src')
                    video=None
                else:
                    image=None
                    video=None
            recipe['tasks'].append({"title":title,"instruction":instruction.replace('\n',''),"image":image,"video":video})
        
        taglist=soup.find_all(class_="tag-unit flex body-3 justify-center align-center text-center secondary-button")
        recipe['tags']=[]
        for item in taglist:
            recipe['tags'].append(item.text.strip())

        recipes.append(recipe)

    with open(f'{mealtype}.json', 'w') as f:
        json.dump(recipes, f)


        

