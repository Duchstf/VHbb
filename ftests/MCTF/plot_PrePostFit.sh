#Define the poly orders
pt=0
rho=1
year=2016

cd $year/pt${pt}rho${rho}/

conda run -n combine --no-capture-output combine -M FitDiagnostics -m 125 output/testModel_$year/model_combined.root --saveShapes --saveWithUncertainties --cminDefaultMinimizerStrategy 0 --robustFit=1

cd ../../scripts/

conda run -n plot --no-capture-output python plot_PrePostFit.py --pt $pt --rho $rho --year $year

cd ..