1. Produce toys and calculates the goodness of fit for each polynomial order (0,rho) and (0,rho+1). 

```
./run_jobs.sh <year>
```

2. When the jobs have finished, do
``` 
./do_ftest.sh 0 $rho
```

Start from pT=0,rho=0. If the F-test statistic has p-value < 5%, take the higher order polynomial as baseline and repeat. Stop when the higher order polynomials all have p-value > 5%. 

3. After determining the optimal order, fo into `plot_PrePostFit.sh` and plug in the year, pt, rho you want to plot. 

Repeat for all years.