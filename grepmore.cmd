@Rem "pattern" filespec
@Rem Echo grep [%1] -- %2 %3 %4 %5 %6 %7 %8 %9
@for %%f in (%2 %3 %4 %5 %6 %7 %8 %9) do grep %1 %%f