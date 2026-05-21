import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";

export const useHealth = () =>
  useQuery({ queryKey: ["health"], queryFn: api.health, refetchInterval: 10000 });

export const useUsers = (limit = 50) =>
  useQuery({ queryKey: ["users", limit], queryFn: () => api.listUsers(limit) });

export const useWeibo = (uid?: number, limit = 50) =>
  useQuery({ queryKey: ["weibo", uid, limit], queryFn: () => api.listWeibo(uid, limit) });

export const useTasks = () =>
  useQuery({ queryKey: ["tasks"], queryFn: api.listTasks, refetchInterval: 4000 });

export const useSearch = (q: string) =>
  useQuery({
    queryKey: ["search", q],
    queryFn: () => api.search(q),
    enabled: q.length >= 1,
  });

export const useCreateTask = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.createTask,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tasks"] }),
  });
};
