% This script generates the A and A_bar matrices used in GDP. A is used for
% the steady GDP and A_bar is used for transient GDP. 

% User can specify the power budgeting time step in t_budget, which should
% be the same as the dvfs_epoch in base.cfg: for example, t_budget = 0.001
% and dvfs_epoch = 1000000 means power budget is updated every 1ms.

% G, C, B matrices need to extracted from HotSpot with a floorplan first.

name_of_chip = '8x8';
% set the power budgeting time step, works for transient GDP (A_bar)
t_budget = 0.001; 

load(strcat(name_of_chip,'_G.mat'));
load(strcat(name_of_chip,'_C.mat'));
load(strcat(name_of_chip,'_B.mat'));

% compute A matrix for steady state GDP
A = full(B'*(G\B));
save(strcat(name_of_chip,'_A.mat'), 'A');

% compute A_bar matrix for transient GDP with power budget step t_budget
Ac = full(- (C \ G));
Bc = full(C \ B) ;
Cc = full(B');
Dc = zeros(size(A,1), size(A,1));
[M,N,L,~] = c2dm(Ac,Bc,Cc,Dc,t_budget); % M and N matrices in GDP paper
A_bar = B'*N;

save(strcat(name_of_chip,'_A_',string(t_budget*1000),'ms.mat'), 'A_bar');