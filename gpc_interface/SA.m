function [Ti, Tall]=SA(model, dim)
%input:
% dim = total number of random parameters
% model = the output of ST_run.m 
%output:
%Ti and Tall is a vector whose length is dim. 
%The ith entry in Ti and Tall represent the main sensitivity and total sensitivity of parameter i.

model.gPC=model.gPC';
gPC=model.gPC(:,2:end);

%% total variance of the output
valT=sum(gPC.^2);
index=model.pcIndex(:,2:end);
N=size(gPC,2);

%% Sobol sensitivity analysis
Ti=zeros(1,dim); %main sensitivity
Tall=zeros(1,dim); % total sensitivity


for j=1:N
    ind=index(:,j); id=find(ind>0);
    if length(id)==1
        Ti(id)=Ti(id)+gPC(j)^2;
        Tall(id)=Tall(id)+gPC(j).^2;
    else
        Tall(id)=Tall(id)+gPC(j).^2;
    end
end

Ti=Ti/valT;
Tall=Tall/valT;
%k=1:dim;

% plot(k,Ti,'b', k, Tall,'r');
% 
% figure;
% subplot(1,2,1); pie(Ti);
% subplot(1,2,2); pie(Tall);
% 
% figure;
% subplot(1,2,1); plot(k,Ti);
% subplot(1,2,2); plot(k,Tall);
% 
% figure;
% bar(k,[Ti' Tall']); 
% legend('main sensitivity','total sensitivity');
% xlim([0,dim]); xlabel('Parameter index')
