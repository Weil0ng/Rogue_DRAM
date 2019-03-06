clear all; clc; 
load('anovaModel90.mat');


gPC=model.gPC(:,2:end);

%% total variance of the output
valT=sum(gPC.^2);
index=model.pcIndex(:,2:end);
N=size(gPC,2);

dim=46; % total number of random parameters

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

Ti=Ti/valT; Tall=Tall/valT;
k=1:dim;

plot(k,Ti,'b', k, Tall,'r');

figure;
subplot(1,2,1); pie(Ti);
subplot(1,2,2); pie(Tall);

figure;
subplot(1,2,1); plot(k,Ti);
subplot(1,2,2); plot(k,Tall);

figure;
bar(k,[Ti' Tall']); 
legend('main sensitivity','total sensitivity');
xlim([0,dim]); xlabel('Parameter index')