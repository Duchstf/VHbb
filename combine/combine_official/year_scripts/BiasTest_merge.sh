for bias in {1..5}
    do 
    hadd -f bias$bias.root *Combinebias$bias.*
    done