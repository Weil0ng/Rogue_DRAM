function model=gpc_model(model, y)

y = transpose(cell2mat(y));
gPC=model.gpcMapMatrixInv*y;
model.gPC=gPC;
model.meanVal=gPC(1);
model.stdVal=realsqrt(sum(gPC(2:end).^2));
model.type='pce';

end
