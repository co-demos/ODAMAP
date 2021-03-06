import pandas as pd
print("Load effectif + siren data")
dfeff = pd.read_csv("../data/simu-effectifs/effectif.csv")
dfsiren = pd.read_csv("../data/extracts/extract-siren.csv", dtype={'reg':str, 'dep':str, 'arr':str,'codecommuneetablissement':str})
print("merging effectif and siren based on siret")
dfmerge = pd.merge(dfsiren, dfeff, on='siret', how='left')
print("group by unique siren and get sum of effectif")
dfmerge2 = dfmerge.groupby(['siren'], as_index = False).sum()
print("exclude siren where effectif < 40 to focus on TPE/PME")
dfmerge3 = dfmerge2[dfmerge2['effectif'] < 40]
print("generate random subset of 250k for simulating aide")
random_subset = dfmerge3.sample(n=250000)
dfintermediary = random_subset.drop(columns=['siret'])
print("building columns for final dataset")
dfintermediary['code_application'] = "Volet1"
dfintermediary['mois'] = "mars"
dfintermediary['nom1'] = "Martin"
dfintermediary['nom2'] = None
dfintermediary['nombre_salarie'] = dfintermediary['effectif']
dfintermediary['devise'] = "euros"
dfintermediary['date_dp'] = "2020-03-10"
dfintermediary['date_paiement'] = "2020-03-25"
dfintermediary['montant'] = 1500
dfintermediary['numero_sequentiel'] = dfintermediary['siren'].astype(str)+"XXX"
dfintermediary = dfintermediary[['code_application', 'numero_sequentiel', 'mois', 'siren', 'nom1', 'nom2', 'effectif', 'montant','devise','date_dp','date_paiement']]
print("merging with siren data to get geo data for each aide")
dfintermediary2 = pd.merge(dfintermediary, dfsiren, on='siren', how='left')
print("count number of unique siret per siren to dispatch montant equitably")
inter = dfintermediary2.groupby(['siren'], as_index = False).count()
inter = inter[['siren','numero_sequentiel']]
inter.rename(columns={'numero_sequentiel':'count_siren_nb'},inplace=True)
print("merging dataframe with those number of siret per siren")
dfintermediary3 = pd.merge(dfintermediary2, inter, on='siren', how='left')
print("calculate adjusted montant depending on how much siret there is in a siren")
dfintermediary3['montant_modifie'] = dfintermediary3['montant'] / dfintermediary3['count_siren_nb']
print("final make up")
dfintermediary3.dep = dfintermediary3.dep.astype(str)
dfintermediary3['dep'] = dfintermediary3['dep'].apply(lambda x: x.split(".0")[0])
dfintermediary3['reg'] = dfintermediary3['reg'].astype(str)
dfintermediary3['dep'] = dfintermediary3['dep'].astype(str)
dfintermediary3['codecommuneetablissement'] = dfintermediary3['codecommuneetablissement'].astype(str)
dfaide = dfintermediary3
print("calculate delta effectif for each siret and its percentage")
dfeff['delta_effectif'] = dfeff['effectif2'] - dfeff['effectif']
dfeff['delta_effectif_percent'] = dfeff['delta_effectif'] / dfeff['effectif']
dfeff['delta_effectif_percent'] = dfeff['delta_effectif_percent'].apply(lambda x: x if pd.notna(x) else 0)
dfeff.siret = dfeff.siret.astype(str)
dfaide.siret = dfaide.siret.astype(str)
dfeff = dfeff[['siret','delta_effectif', 'delta_effectif_percent']]
print("merging with aide dataframe")

dfaide = pd.merge(dfaide, dfeff, on='siret', how='left')
print("create a category for each type of effectif")
dfaide['classe_effectif'] = dfaide['effectif'].apply(lambda x: '00' if x == 0 else '01' if x <= 2 else '02' if x <= 5 else '03' if x <= 9 else '11' if x <= 19 else '12' if x <= 49 else '21' if x <= 99 else '22' if x <= 199 else '31' if x <= 249 else '32' if x <= 499 else '41' if x <= 999 else '42' if x <= 1999 else '51' if x <= 4999 else '52' if x <= 9999 else '53')

#A vérifier
dfaide['reg'] = dfaide['reg'].apply(lambda x: x.split(".0")[0])
dfaide['reg'] = dfaide['reg'].apply(lambda x: None if x == 'nan' else x)
dfaide['dep'] = dfaide['dep'].apply(lambda x: x.split(".0")[0])
dfaide['dep'] = dfaide['dep'].apply(lambda x: None if x == 'nan' else x)
dfaide['codecommuneetablissement'] = dfaide['codecommuneetablissement'].apply(lambda x: x.split(".0")[0])
dfaide['codecommuneetablissement'] = dfaide['codecommuneetablissement'].apply(lambda x: None if x == 'nan' else x)

print("saving csv")
dfaide.to_csv("../data/simu-aides/aides.csv", index=False)