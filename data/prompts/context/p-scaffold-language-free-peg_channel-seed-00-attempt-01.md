## Search State

- **Seed**: 0
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2471 | 0.78 | ❌ rejected |
| 0 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2437 | 0.83 | ✅ accepted |

**Proposal policy**: task_score is 0.78 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_channel
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.833, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5109569349857164, 0.061582937101109625, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5109569349857164, -0.09841706289889038, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.247) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.247
- **task_score** (E): 0.784
- **fitness_score**: 0.687  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2615 |
| approach_1 | 1.00 | 1.00 | 0.0099 |
| contact_1 | 1.00 | 1.00 | 0.0114 |
| push_1 | 0.67 | 1.00 | 0.1568 |
| retract_1 | 0.00 | 1.00 | 0.1061 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.125, 0.051) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.333 | 111.931 | 119.907 |
| approach_1 | approach | 1.00 / step_budget | (0.495, 0.125, 0.051)→(0.496, 0.122, 0.042) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.333 | 39.219 | 141.478 |
| contact_1 | contact | 1.00 / step_budget | (0.496, 0.122, 0.042)→(0.497, 0.114, 0.036) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.160 | 1.00 / 2.333 | 141.578 | 159.378 |
| push_1 | push | 0.67 / step_budget | (0.497, 0.114, 0.036)→(0.499, -0.043, 0.037) | (0.500, 0.080, 0.034)→(0.503, -0.072, 0.036) | 0.160→0.018 | 1.00 / 3.000 | 37.464 | 124.997 |
| retract_1 | retract | 0.00 / step_budget | (0.499, -0.043, 0.037)→(0.496, -0.000, 0.134) | (0.503, -0.072, 0.036)→(0.502, -0.069, 0.034) | 0.018→0.017 | 1.00 / 1.000 | 0.547 | 71.177 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.893
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.821
- phase_score: 0.659
- phase_breakdown.approach_score: 0.856
- phase_breakdown.push_score: 0.583
- phase_breakdown.contact_score: 0.691

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.724
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.980
- **Median Q (composite search score)**: 0.255
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.457


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50588,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00395,"approach_1.approach_height":0.25658,"contact_1.contact_force":9.89074,"push_1.push_distance":0.12651,"push_1.push_speed":0.09252,"retract_1.retract_height":0.13536,"retract_1.speed":0.07126},"optimized_scores":{"best_composite_score":0.28372,"best_fitness_score":0.72372,"best_task_score":0.82093},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.10482,0.06],"force_p95":116.55472,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.55472,"mean_force":116.55472,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50457,0.10474,0.04324]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":687.0,"contact_point_centroid":[0.5445,0.02682,0.05999],"force_p95":102.91825,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.84782,"mean_force":83.63344,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49974,0.02871,0.03669]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":327.0,"contact_point_centroid":[0.54556,0.0976,0.05997],"force_p95":113.6143,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.42509,"mean_force":77.26061,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50097,0.09694,0.03612]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":246.0,"contact_point_centroid":[0.52502,0.09709,0.05999],"force_p95":112.31273,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.94108,"mean_force":79.56813,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50103,0.09694,0.03618]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52502,0.09679,0.05999],"force_p95":65.25959,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.69787,"mean_force":22.82806,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50101,0.09665,0.03613]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54289,-0.04924,0.05999],"force_p95":69.23985,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.04936,"mean_force":59.50059,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49822,-0.05328,0.03673]},{"body_a":"attachment","body_b":"peg","contact_count":414.0,"contact_point_centroid":[0.50322,-0.00041,0.04214],"force_p95":18.76179,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.0734,"mean_force":4.41595,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49944,0.0113,0.03674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":26.0,"contact_point_centroid":[0.50688,-0.10033,0.0603],"force_p95":29.72148,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.62424,"mean_force":17.77261,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4982,-0.0521,0.03674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":723.0,"contact_point_centroid":[0.50293,-0.01157,0.00969],"force_p95":13.34024,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.30389,"mean_force":2.29731,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49977,0.02973,0.0367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":26.0,"contact_point_centroid":[0.50618,-0.10025,0.0606],"force_p95":5.9973,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.70749,"mean_force":1.39552,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49727,-0.05188,0.03806]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.5052,-0.06464,0.05066],"force_p95":6.76855,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.16299,"mean_force":1.78983,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49777,-0.0529,0.03711]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":52.0,"contact_point_centroid":[0.47491,0.01437,0.02553],"force_p95":1.48621,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.80868,"mean_force":0.52996,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50011,0.04548,0.03678]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":246.0,"contact_point_centroid":[0.52519,-0.03215,0.03162],"force_p95":3.35327,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.71201,"mean_force":0.79151,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49928,-0.0027,0.03681]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52503,-0.08273,0.06],"force_p95":2.67643,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.68777,"mean_force":2.20148,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49821,-0.05329,0.03674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":812.0,"contact_point_centroid":[0.50369,0.06161,0.00935],"force_p95":0.64051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55646,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50246,0.15146,0.16945]},{"body_a":"peg","body_b":"channel_base_body","contact_count":975.0,"contact_point_centroid":[0.50447,-0.08109,0.0094],"force_p95":0.55756,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01427,"mean_force":0.54917,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49504,-0.02306,0.09112]}],"total_contact_groups":19},"final_pose_error":0.15374,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50427,-0.08129,0.034],"final_tcp_position":[0.49577,-0.00314,0.14635],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":116.55472,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.06154,0.03379],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14173,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.5445,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":831.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.50647,0.10562,0.04772],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":23.0,"n_steps_budget":600.0,"object_pos_end":[0.50379,0.06161,0.03379],"object_pos_start":[0.50377,0.06154,0.03379],"object_to_goal_dist_end":0.14179,"object_to_goal_dist_start":0.14173,"object_z_max":0.03379,"peak_contact_force":116.55472,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":116.55472,"tcp_end":[0.50449,0.10469,0.043],"tcp_start":[0.50647,0.10562,0.04772],"tcp_to_object_dist_end":0.04406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":406.0,"n_steps_budget":600.0,"object_pos_end":[0.50379,0.06157,0.0338],"object_pos_start":[0.50379,0.06161,0.03379],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14179,"object_z_max":0.0338,"peak_contact_force":114.42509,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":979.0,"raw_peak_contact_force":114.42509,"tcp_end":[0.50101,0.09668,0.03611],"tcp_start":[0.50449,0.10469,0.043],"tcp_to_object_dist_end":0.03529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,-0.08188,0.03645],"object_pos_start":[0.50379,0.06157,0.0338],"object_to_goal_dist_end":0.00733,"object_to_goal_dist_start":0.14176,"object_z_max":0.03774,"peak_contact_force":21.38624,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2155.0,"raw_peak_contact_force":114.84782,"tcp_end":[0.49822,-0.05324,0.03673],"tcp_start":[0.50101,0.09668,0.03611],"tcp_to_object_dist_end":0.02971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50427,-0.08129,0.034],"object_pos_start":[0.50614,-0.08188,0.03645],"object_to_goal_dist_end":0.00748,"object_to_goal_dist_start":0.00733,"object_z_max":0.03652,"peak_contact_force":0.54748,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1025.0,"raw_peak_contact_force":70.04936,"tcp_end":[0.49577,-0.00314,0.14635],"tcp_start":[0.49822,-0.05324,0.03673],"tcp_to_object_dist_end":0.13712,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00382,"approach_1.approach_height":0.18983,"contact_1.contact_force":11.31853,"push_1.push_distance":0.19768,"push_1.push_speed":0.09999,"retract_1.retract_height":0.18724,"retract_1.speed":0.04849},"optimized_scores":{"best_composite_score":0.25515,"best_fitness_score":0.69515,"best_task_score":0.98004},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":755.0,"contact_point_centroid":[0.5436,0.0672,0.05999],"force_p95":121.92532,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.47384,"mean_force":102.69587,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49794,0.07134,0.03634]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":283.0,"contact_point_centroid":[0.54773,0.12,0.05998],"force_p95":128.3165,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.33072,"mean_force":80.04581,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49551,0.14659,0.0343]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54341,-0.02143,0.06],"force_p95":69.28395,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.7522,"mean_force":56.06966,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49872,-0.01622,0.0369]},{"body_a":"attachment","body_b":"peg","contact_count":394.0,"contact_point_centroid":[0.50259,0.05988,0.0414],"force_p95":21.43493,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.24038,"mean_force":4.06305,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49791,0.07139,0.03631]},{"body_a":"peg","body_b":"channel_base_body","contact_count":708.0,"contact_point_centroid":[0.50469,0.02829,0.00967],"force_p95":15.48146,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.23969,"mean_force":2.58508,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49797,0.07042,0.03634]},{"body_a":"peg","body_b":"channel_base_body","contact_count":418.0,"contact_point_centroid":[0.50076,0.11464,0.00945],"force_p95":0.65217,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.27037,"mean_force":0.63327,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49521,0.1481,0.0352]},{"body_a":"attachment","body_b":"peg","contact_count":46.0,"contact_point_centroid":[0.50067,0.13372,0.04272],"force_p95":2.79028,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.98287,"mean_force":1.04541,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49668,0.14564,0.03421]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":293.0,"contact_point_centroid":[0.52526,0.03928,0.03273],"force_p95":3.84506,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.57273,"mean_force":0.87411,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49796,0.06871,0.03645]},{"body_a":"peg","body_b":"channel_base_body","contact_count":755.0,"contact_point_centroid":[0.50092,0.11599,0.00939],"force_p95":0.61661,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55392,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4977,0.17803,0.1717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5063,-0.04413,0.00942],"force_p95":0.55178,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83383,"mean_force":0.54459,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49538,0.00215,0.08205]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.50502,-0.02675,0.05225],"force_p95":0.76046,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.40453,"mean_force":0.29247,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49735,-0.01498,0.03862]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50075,0.11655,0.00946],"force_p95":0.5787,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58479,"mean_force":0.54094,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49639,0.15694,0.04619]}],"total_contact_groups":12},"final_pose_error":0.1716,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50632,-0.0437,0.03399],"final_tcp_position":[0.49581,0.01432,0.12905],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":134.47384,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11605,0.03394],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54801,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":755.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49706,0.15726,0.04892],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":28.0,"n_steps_budget":600.0,"object_pos_end":[0.50092,0.11601,0.03391],"object_pos_start":[0.50095,0.11605,0.03394],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19615,"object_z_max":0.03394,"peak_contact_force":0.54838,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28.0,"raw_peak_contact_force":0.58479,"tcp_end":[0.49634,0.15677,0.04264],"tcp_start":[0.49706,0.15726,0.04892],"tcp_to_object_dist_end":0.04193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":418.0,"n_steps_budget":600.0,"object_pos_end":[0.50145,0.11511,0.03456],"object_pos_start":[0.50092,0.11601,0.03391],"object_to_goal_dist_end":0.1952,"object_to_goal_dist_start":0.19611,"object_z_max":0.03456,"peak_contact_force":103.05412,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":747.0,"raw_peak_contact_force":131.33072,"tcp_end":[0.49714,0.14524,0.03415],"tcp_start":[0.49634,0.15677,0.04264],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50639,-0.04491,0.03567],"object_pos_start":[0.50145,0.11511,0.03456],"object_to_goal_dist_end":0.03592,"object_to_goal_dist_start":0.1952,"object_z_max":0.0382,"peak_contact_force":91.00546,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2150.0,"raw_peak_contact_force":134.47384,"tcp_end":[0.49873,-0.01609,0.0369],"tcp_start":[0.49714,0.14524,0.03415],"tcp_to_object_dist_end":0.02985,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50632,-0.0437,0.03399],"object_pos_start":[0.50639,-0.04491,0.03567],"object_to_goal_dist_end":0.03733,"object_to_goal_dist_start":0.03592,"object_z_max":0.03606,"peak_contact_force":0.54223,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1029.0,"raw_peak_contact_force":70.7522,"tcp_end":[0.49581,0.01432,0.12905],"tcp_start":[0.49873,-0.01609,0.0369],"tcp_to_object_dist_end":0.11186,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39326,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.0041,"approach_1.approach_height":0.13926,"contact_1.contact_force":7.79479,"push_1.push_distance":0.16873,"push_1.push_speed":0.09982,"retract_1.retract_height":0.1997,"retract_1.speed":0.05056},"optimized_scores":{"best_composite_score":0.20252,"best_fitness_score":0.64252,"best_task_score":0.5496},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":60.0,"contact_point_centroid":[0.4749,0.12,0.0598],"force_p95":341.5277,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.62701,"mean_force":311.80708,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47984,0.111,0.05723]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":30.0,"contact_point_centroid":[0.47497,0.11792,0.05994],"force_p95":283.70214,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.29523,"mean_force":209.67753,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48303,0.11067,0.05591]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":409.0,"contact_point_centroid":[0.535,0.10349,0.05995],"force_p95":214.24986,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.3783,"mean_force":173.94326,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48947,0.10213,0.03793]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":725.0,"contact_point_centroid":[0.54103,0.02216,0.05999],"force_p95":116.32392,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":125.66889,"mean_force":95.77413,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4957,0.02366,0.03784]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54357,-0.0562,0.05999],"force_p95":72.48285,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.72901,"mean_force":71.08004,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49854,-0.05995,0.03737]},{"body_a":"attachment","body_b":"peg","contact_count":348.0,"contact_point_centroid":[0.49619,-0.00465,0.03877],"force_p95":43.60126,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.67832,"mean_force":8.72127,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49625,0.00706,0.0378]},{"body_a":"peg","body_b":"channel_base_body","contact_count":66.0,"contact_point_centroid":[0.4952,-0.10162,0.03633],"force_p95":56.27646,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.18728,"mean_force":34.35607,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49822,-0.05614,0.03744]},{"body_a":"attachment","body_b":"peg","contact_count":80.0,"contact_point_centroid":[0.49577,-0.06726,0.04045],"force_p95":26.21667,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.24422,"mean_force":12.90248,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49663,-0.05557,0.04008]},{"body_a":"peg","body_b":"channel_base_body","contact_count":98.0,"contact_point_centroid":[0.49389,-0.10125,0.0557],"force_p95":25.56018,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.19988,"mean_force":11.36603,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49633,-0.05453,0.04129]},{"body_a":"peg","body_b":"channel_base_body","contact_count":746.0,"contact_point_centroid":[0.49773,-0.01223,0.00968],"force_p95":9.58017,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.82372,"mean_force":1.84768,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49565,0.02475,0.03785]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":384.0,"contact_point_centroid":[0.47478,-0.01802,0.0247],"force_p95":1.17574,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.29459,"mean_force":0.47834,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49612,0.01237,0.03788]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":47.0,"contact_point_centroid":[0.47494,-0.08313,0.06],"force_p95":6.91728,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.69765,"mean_force":3.86781,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49574,-0.05322,0.04181]},{"body_a":"peg","body_b":"channel_base_body","contact_count":820.0,"contact_point_centroid":[0.49531,0.0638,0.00938],"force_p95":0.56258,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55591,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48773,0.15105,0.1656]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49933,0.19869,0.29695]},{"body_a":"peg","body_b":"channel_base_body","contact_count":910.0,"contact_point_centroid":[0.49607,-0.08136,0.00939],"force_p95":0.58435,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07965,"mean_force":0.55108,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49513,-0.03021,0.08468]},{"body_a":"peg","body_b":"channel_base_body","contact_count":439.0,"contact_point_centroid":[0.49515,0.0639,0.0094],"force_p95":0.55087,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54517,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4894,0.10228,0.03802]}],"total_contact_groups":17},"final_pose_error":0.17419,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49597,-0.08138,0.03379],"final_tcp_position":[0.49566,-0.01258,0.12632],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":355.62701,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.49535,0.06392,0.03399],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":334.70153,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":908.0,"raw_peak_contact_force":355.62701,"tcp_end":[0.481,0.11081,0.05671],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":95.0,"n_steps_budget":600.0,"object_pos_end":[0.49532,0.06402,0.034],"object_pos_start":[0.49535,0.06392,0.03399],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14412,"object_z_max":0.034,"peak_contact_force":0.55289,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":125.0,"raw_peak_contact_force":307.29523,"tcp_end":[0.48856,0.10593,0.04095],"tcp_start":[0.481,0.11081,0.05671],"tcp_to_object_dist_end":0.04301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":439.0,"n_steps_budget":600.0,"object_pos_end":[0.49527,0.06412,0.03403],"object_pos_start":[0.49532,0.06402,0.034],"object_to_goal_dist_end":0.14432,"object_to_goal_dist_start":0.14422,"object_z_max":0.03403,"peak_contact_force":207.25489,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":848.0,"raw_peak_contact_force":232.3783,"tcp_end":[0.49312,0.0992,0.03757],"tcp_start":[0.48856,0.10593,0.04095],"tcp_to_object_dist_end":0.03533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4953,-0.08879,0.03521],"object_pos_start":[0.49527,0.06412,0.03403],"object_to_goal_dist_end":0.01106,"object_to_goal_dist_start":0.14432,"object_z_max":0.03896,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2269.0,"raw_peak_contact_force":125.66889,"tcp_end":[0.49861,-0.05983,0.0374],"tcp_start":[0.49312,0.0992,0.03757],"tcp_to_object_dist_end":0.02923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49597,-0.08138,0.03379],"object_pos_start":[0.4953,-0.08879,0.03521],"object_to_goal_dist_end":0.00753,"object_to_goal_dist_start":0.01106,"object_z_max":0.03738,"peak_contact_force":0.55086,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1138.0,"raw_peak_contact_force":72.72901,"tcp_end":[0.49566,-0.01258,0.12632],"tcp_start":[0.49861,-0.05983,0.0374],"tcp_to_object_dist_end":0.1153,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```