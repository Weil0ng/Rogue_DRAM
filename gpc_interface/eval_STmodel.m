function y=eval_STmodel(model,X)

if iscell(X)
    X = transpose(cell2mat(X));
end

paraDef=model.paraDef;
for m=1:length(paraDef.type) %%Normalize physical points
    type=paraDef.type(m);
        switch lower(type{1})
            case 'truncated_gaussian'
                X(m,:) = (X(m,:) - paraDef.pdfPara{m}(1)) / paraDef.pdfPara{m}(2);
            case 'gaussian'
                X(m,:) = (X(m,:) - paraDef.pdfPara{m}(1)) / paraDef.pdfPara{m}(2);
        end
end

%Using the obtained results from stochastic spectral methods, to extract
%the density function of y.
pcNum=model.pcBasisNum;
gPC=model.gPC;
if size(gPC,2)>1
    gPC=gPC.';
end
stateNum=floor(length(gPC)/pcNum);
gPC=reshape(gPC,[pcNum,stateNum]);
N=size(X,2); y=zeros(N,stateNum);
% X para*sample
for k=1:N %sample numebr
H=evalGPCSeries(model,X(:,k));
y(k,:)=H*gPC;
end
y=y.';
