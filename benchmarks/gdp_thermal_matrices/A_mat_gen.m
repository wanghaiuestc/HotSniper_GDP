load('8x8_G.mat');
load('8x8_C.mat');
load('8x8_B.mat');
t_budget = 0.001; % power budgeting time step

A = full(B'*(G\B));
save('8x8_A.mat', 'A');

Ac = full(- (C \ G));
Bc = full(C \ B) ;
Cc = full(B');
Dc = zeros(64,64);
[M,N,L,~] = c2dm(Ac,Bc,Cc,Dc,t_budget);
A_bar = B'*N;

save('8x8_A_1ms.mat', 'A_bar');