for bias in {0..5}
    do 
    hadd -f bias$bias.root *Combinebias$bias.*
    done