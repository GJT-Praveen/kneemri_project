from temp import predict_diagnosis

if __name__ =='__main__':
    abnormal,acl,meniscus=predict_diagnosis()
    print(abnormal)
    print(acl)
    print(meniscus)