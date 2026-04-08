

Python 3.10.13

pip install  -r requirements.txt



HOW TO:

On-the-fly 2D Similarity:


1. Simplest (Without Result images .png)

   Example input:
      number cpu usage = 100
      top rank = 1000
      # input query smile = "CCCOc1ccc(OC(=O)c2cccc([N+](=O)[O-])c2)cc1"
      input query smile = "C#Cc1cc(Nc2c3cc(OCCOC)c(OCCOC)cc3ncn2)ccc1"
      library dataset = "./example/CHEMBL29_part1-364620.smi"
      save result csv = "./result/similarity-result.csv"


      # python similarity.py --is-show-time-open-file --is-show-time-logic --cpu 100 --rank 1000 --smile "CCCOc1ccc(OC(=O)c2cccc([N+](=O)[O-])c2)cc1" --lib example/CHEMBL29_part1-364620.smi --save-to result/similarity-result.csv
      python similarity.py --is-show-time-open-file --is-show-time-logic --cpu 100 --rank 1000 --smile "C#Cc1cc(Nc2c3cc(OCCOC)c(OCCOC)cc3ncn2)ccc1" --lib example/CHEMBL29_part1-364620.smi --save-to result/similarity-result.csv

      
2. Output contain .pngs (we limited maximum rank to 9999 rank molecules)
   
      # python similarity.py --is-need-pngs --is-show-time-open-file --is-show-time-logic --cpu 100 --rank 1000 --smile "CCCOc1ccc(OC(=O)c2cccc([N+](=O)[O-])c2)cc1" --lib example/CHEMBL29_part1-364620.smi --save-to result/similarity-result.csv
      python similarity.py --is-need-pngs --is-show-time-open-file --is-show-time-logic --cpu 100 --rank 1000 --smile "C#Cc1cc(Nc2c3cc(OCCOC)c(OCCOC)cc3ncn2)ccc1" --lib example/CHEMBL29_part1-364620.smi --save-to result/similarity-result.csv




On-the-fly 2D Substructure:


1. Simples (Without Result images .png)

   Example input:
      number cpu usage = 100
      top rank = 1000
      input query smile = "c1ccccc1Nc2ncnc(c23)cccc3"
      library dataset = "./example/CHEMBL29_part1-364620.smi"
      save result csv = "./result/substructure-result.csv"


      python substructure.py --is-show-time-open-file --is-show-time-logic --cpu 100 --rank 1000 --smile "c1ccccc1Nc2ncnc(c23)cccc3" --lib example/CHEMBL29_part1-364620.smi --save-to result/substructure-result.csv

      
2. Output contain .pngs (we limited maximum rank to 9999 rank molecules)

      python substructure.py --is-need-pngs --is-show-time-open-file --is-show-time-logic --cpu 100 --rank 1000 --smile "c1ccccc1Nc2ncnc(c23)cccc3" --lib example/CHEMBL29_part1-364620.smi --save-to result/substructure-result.csv
