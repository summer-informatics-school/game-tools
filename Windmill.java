import java.io.*;
import java.util.*;

public class Windmill {
	public static final String TABLES_NAMES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ23456789";//abdefghijkmnpqrt";
	public static final char ABSENT = '-';
	public static final char DELIM = '.';
	public static final int MAX_TABLES = TABLES_NAMES.length();
	public static final int TABLE_SIZE = 6;
	public static final int MAX_PLAYERS = MAX_TABLES * TABLE_SIZE;
	public static final int ROUNDS = 8;
	public static final int SERIES = 4;
	public static final int QUESTIONS = ROUNDS * SERIES;
	
	public static void main(String[] args) throws IOException {
		Random random = new Random(566);
		StringBuilder[] sb = new StringBuilder[MAX_PLAYERS];
		for (int i = 0; i < MAX_PLAYERS; i++) {
			String playerString = String.format("%0" + ("" + MAX_PLAYERS).length() + "d", i + 1);
			sb[i] = new StringBuilder("Player " + playerString + ".\t Name: \n\n\n").
					append("Player " + playerString + ".\n");
		}
		for (int tables = 1; tables <= MAX_TABLES; tables++) {
			int players = tables * TABLE_SIZE;
			for (int i = 0; i < MAX_PLAYERS; i++) {
				String playersString = String.format("%0" + ("" + MAX_PLAYERS).length() + "d", players);
				sb[i].append(playersString + ": ");
			}
			int[] withEmpties = new int[players];
			ArrayList<ArrayList<Character>> lists = new ArrayList<>();
			for (int round = 0; round < ROUNDS; round++) {
				ArrayList<Character> list = new ArrayList<>();
				for (int i = 0; i < tables; i++) {
					for (int j = 0; j < TABLE_SIZE; j++) {
						list.add(TABLES_NAMES.charAt(i));
					}
				}
				ArrayList<Character> best = null;
				double bestPenaly = Double.MAX_VALUE;
				//main:
				for (int iter = 0; iter < 1024; iter++) {
					Collections.shuffle(list, random);
					double penalty = 0;
					for (int i = 0; i < TABLE_SIZE - 1; i++) {
						for (int j = 0; j < i; j++) {
							if (list.get(players - 1 - i) == list.get(players - 1 - j)) {
								penalty += 1e9;
							}
						}
					}
					for (int i = 0; i < players - TABLE_SIZE + 1; i++) {
						for (int j = players - TABLE_SIZE + 1; j < players; j++) {
							if (list.get(i) == list.get(j)) {
								penalty += withEmpties[i] * 1e7;
							}
						}
					}

					
					if (penalty < bestPenaly) {
						best = new ArrayList<>(list);
						bestPenaly = penalty;
					}
				}
				list = best;
				lists.add(list);
				for (int i = 0; i < players - TABLE_SIZE + 1; i++) {
					for (int j = players - TABLE_SIZE + 1; j < players; j++) {
						if (list.get(i) == list.get(j)) {
							withEmpties[i]++;
						}
					}
				}
				for (int i = 0; i < MAX_PLAYERS; i++) {
					char c = (i < players) ? list.get(i) : ABSENT;
					sb[i].append(c);
					if (round + 1 < ROUNDS && (round + 1) % 4 == 0) {
						sb[i].append(DELIM);
					}
					if (i < players) {
						
					}
				}
			}
			for (int i = 0; i < MAX_PLAYERS; i++) {
				sb[i].append("; ");
			}
			
			{
				PrintWriter pw = new PrintWriter("~table" + players + ".csv");
				String[][] sheet = new String[players][3 + QUESTIONS + ROUNDS];
				for (int i = 0; i < sheet.length; i++) {
					Arrays.fill(sheet[i], "");
				}
				int x = 0, y = 0;
				for (int i = 0; i < tables; i++) {
					sheet[x + i][y] = "Table " + TABLES_NAMES.charAt(i);
				}
				for (int i = 0; i < QUESTIONS; i++) {
					sheet[x + tables][y + 1 + i] = "" + (i + 1);
				}
				y += 1 + QUESTIONS;
				for (int i = 0; i < players; i++) {
					sheet[x + i][y] = "Player " + (i + 1);
					for (int j = 0; j < ROUNDS; j++) {
						StringBuilder formula = new StringBuilder();
						for (int k = 0; k < SERIES; k++) {
							formula.append(k == 0 ? "=" : "+");
							char tableName = lists.get(j).get(i);
							int xRef = TABLES_NAMES.indexOf(tableName);
							int yRef = 1 + j * SERIES + k;
							formula.append(cell(xRef, yRef));
						}
						sheet[x + i][y + 2 + j] = formula.toString();
					}
					StringBuilder formula = new StringBuilder();
					for (int j = 0; j < ROUNDS; j++) {
						formula.append(j == 0 ? "=" : "+");
						int xRef = x + i;
						int yRef = y + 2 + j;
						formula.append(cell(xRef, yRef));
					}
					sheet[x + i][y + 1] = formula.toString();
				}
				for (String[] row : sheet) {
					for (String cell : row) {
						pw.print(cell + ",");
					}
					pw.println();
				}
				pw.close();
			}
		}
		PrintWriter pw = new PrintWriter("~print.txt");
		for (int i = 0; i < MAX_PLAYERS; i++) {
			sb[i].append("\n\n");
			pw.println(sb[i]);
		}
		pw.close();
	}
	
	static String cell(int x, int y) {
		char from = 'A', to = 'Z' + 1;
		int alphabet = to - from;
		int size = 1;
		for (int len = 1;; len++) {
			size *= alphabet;
			if (y >= size) {
				y -= size;
				continue;
			}
			String s = "";
			for (int i = 0; i < len; i++) {
				s = (char) ('A' + y % alphabet) + s;
				y /= alphabet;
			}
			return s + (x + 1);
		}
	}
}
