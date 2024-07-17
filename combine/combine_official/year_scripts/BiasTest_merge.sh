for bias in 0 1 `seq 5 5 100`
    do 
    hadd -f bias$bias.root *Combinebias$bias.*
    done